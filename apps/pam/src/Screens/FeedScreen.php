<?php

declare(strict_types=1);

namespace App\Screens;

use App\Feed\FeedStore;
use App\Support\Bench;
use App\Support\Page;
use Pam\Native\Component;
use Pam\Native\Element;
use Pam\Native\Http\Http;
use Pam\Native\Http\HttpResponse;
use Pam\Native\ImageFit;
use Pam\Native\Store\Stores;
use Pam\Native\Style;
use Pam\Native\UI\Column;
use Pam\Native\UI\Image;
use Pam\Native\UI\Text;
use Pam\Native\UI\VirtualizedList;

/**
 * Stale-while-revalidate feed: the persisted page renders immediately and a
 * conditional GET (If-None-Match) refreshes it; 304 transfers no body.
 */
final class FeedScreen extends Component
{
    /** @var list<array{id: int, title: string, body: string, image: string}> */
    private array $posts = [];

    private string $source = 'network';

    public function boot(): void
    {
        $store = Stores::get(FeedStore::class);
        $cached = $store->posts;
        if ($cached !== []) {
            $this->posts = $cached;
            $this->source = 'cache';
        }
        $etag = $store->etag;
        Http::request(
            'GET',
            Bench::ASSETS.'/feed.json',
            fn (HttpResponse $response) => $this->received($response, $store),
            headers: $cached !== [] && $etag !== '' ? ['If-None-Match' => $etag] : [],
        );
    }

    public function render(): Element
    {
        if ($this->posts === []) {
            return Page::make();
        }
        $cells = [];
        foreach ($this->posts as $post) {
            $cells[] = Column::make(
                Image::make($post['image'])
                    ->fit(ImageFit::Cover)
                    ->style(new Style(widthPercent: 100, aspectRatio: 1)),
                Text::make($post['title'])->style(new Style(paddingHorizontal: 16, paddingTop: 12, textColor: Bench::TEXT, fontSize: 17, fontWeight: 700)),
                Text::make($post['body'])->style(new Style(paddingHorizontal: 16, paddingTop: 4, paddingBottom: 16, textColor: Bench::TEXT, fontSize: 15)),
            )->key((string) $post['id']);
        }

        return Page::make(
            VirtualizedList::make(...$cells)
                ->estimatedRowHeight(480)
                ->onLayout(fn () => Bench::logOnce('feed', 'ready', scenario: 'feed', source: $this->source))
                ->style(new Style(flexGrow: 1)),
        );
    }

    private function received(HttpResponse $response, FeedStore $store): void
    {
        if ($response->statusCode !== 200) {
            return; // 304: the cached page is current; failures keep what is shown.
        }
        $decoded = json_decode($response->body, true);
        if (!is_array($decoded) || !is_array($decoded['posts'] ?? null)) {
            return;
        }
        $posts = array_map(static fn (array $post): array => [
            'id' => (int) $post['id'],
            'title' => (string) $post['title'],
            'body' => (string) $post['body'],
            'image' => (string) $post['image'],
        ], $decoded['posts']);
        $store->replace($posts, $response->header('ETag') ?? '');
        $this->posts = $posts;
    }
}
