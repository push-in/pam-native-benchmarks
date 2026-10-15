<?php

declare(strict_types=1);

namespace App\Feed;

use Pam\Native\Store\Store;

/** Last good `/feed.json` page and its ETag, persisted across process restarts. */
final class FeedStore extends Store
{
    protected function state(): array
    {
        return ['posts' => [], 'etag' => ''];
    }

    protected function persist(): array
    {
        return ['posts', 'etag'];
    }

    /** @param list<array{id: int, title: string, body: string, image: string}> $posts */
    public function replace(array $posts, string $etag): void
    {
        $this->transaction(function () use ($posts, $etag): void {
            $this->posts = $posts;
            $this->etag = $etag;
        }, 'feed:replace');
    }
}
