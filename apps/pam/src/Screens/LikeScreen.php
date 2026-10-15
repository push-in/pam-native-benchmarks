<?php

declare(strict_types=1);

namespace App\Screens;

use App\Support\Bench;
use App\Support\Page;
use Pam\Native\AccessibilityRole;
use Pam\Native\Align;
use Pam\Native\Component;
use Pam\Native\Element;
use Pam\Native\Justify;
use Pam\Native\Style;
use Pam\Native\UI\Column;
use Pam\Native\UI\Text;
use Pam\Native\UI\TouchableWithoutFeedback;
use Pam\Native\UI\VirtualizedList;

/**
 * 200 rows with a like toggle. The liked set is component state; the Rust
 * reconciler turns each toggle into a patch of the changed row only.
 */
final class LikeScreen extends Component
{
    private const int COUNT = 200;

    /** @var array<int, true> */
    private array $liked = [];

    public function render(): Element
    {
        // Data-driven list (PAM Native 1.45+): a like rebuilds only the shown rows.
        if (method_exists(VirtualizedList::class, 'of')) {
            return Page::make(
                VirtualizedList::of(range(0, self::COUNT - 1), fn (int $i): Element => $this->row($i, isset($this->liked[$i])))
                    ->estimatedRowHeight(72)
                    ->style(new Style(flexGrow: 1)),
            );
        }
        $rows = [];
        for ($i = 0; $i < self::COUNT; $i++) {
            $rows[] = $this->row($i, isset($this->liked[$i]));
        }

        return Page::make(
            VirtualizedList::make(...$rows)
                ->estimatedRowHeight(72)
                ->style(new Style(flexGrow: 1)),
        );
    }

    public function attached(): void
    {
        Bench::log('ready', scenario: 'like');
    }

    public function toggle(int $i): void
    {
        if (isset($this->liked[$i])) {
            unset($this->liked[$i]);
        } else {
            $this->liked[$i] = true;
        }
        Bench::log('like', i: $i, liked: isset($this->liked[$i]) ? 1 : 0);
    }

    private function row(int $i, bool $liked): Element
    {
        $likes = $i * 7 % 50;

        return Column::make(
            Text::make("Post {$i}")->style(Bench::text(16, weight: 700)),
            TouchableWithoutFeedback::make(
                Text::make($liked ? '♥ '.($likes + 1) : "♡ {$likes}")->style(Bench::text(15)),
            )
                ->accessibilityLabel("like-{$i}")
                ->accessibilityRole(AccessibilityRole::Button)
                ->onPress(fn () => $this->toggle($i))
                ->style(new Style(paddingVertical: 6, alignSelf: Align::Start)),
        )->key((string) $i)->style(new Style(
            height: 72,
            paddingHorizontal: 16,
            justifyContent: Justify::Center,
            backgroundColor: $liked ? 0xFFFFE4E6 : Bench::BACKGROUND,
        ));
    }
}
