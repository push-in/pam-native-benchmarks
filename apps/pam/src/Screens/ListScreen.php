<?php

declare(strict_types=1);

namespace App\Screens;

use App\Support\Bench;
use App\Support\Lcg;
use App\Support\Page;
use Pam\Native\Align;
use Pam\Native\Component;
use Pam\Native\Element;
use Pam\Native\Justify;
use Pam\Native\Style;
use Pam\Native\UI\Column;
use Pam\Native\UI\Row;
use Pam\Native\UI\Text;
use Pam\Native\UI\View;
use Pam\Native\UI\VirtualizedList;

/** 10,000 rows of three kinds (i % 3) in one virtualized list. */
final class ListScreen extends Component
{
    private const int COUNT = 10_000;

    public function render(): Element
    {
        // Data-driven list (PAM Native 1.45+), the FlashList renderItem idiom.
        if (method_exists(VirtualizedList::class, 'of')) {
            return Page::make(
                VirtualizedList::of(
                    range(0, self::COUNT - 1),
                    static fn (int $i): Element => match ($i % 3) {
                        0 => self::compact($i),
                        1 => self::avatar($i),
                        default => self::card($i),
                    },
                )
                    ->estimatedRowHeight(72)
                    ->style(new Style(flexGrow: 1)),
            );
        }
        $rows = [];
        for ($i = 0; $i < self::COUNT; $i++) {
            $rows[] = (match ($i % 3) {
                0 => self::compact($i),
                1 => self::avatar($i),
                default => self::card($i),
            })->key((string) $i);
        }

        return Page::make(
            VirtualizedList::make(...$rows)
                ->estimatedRowHeight(72)
                ->style(new Style(flexGrow: 1)),
        );
    }

    public function attached(): void
    {
        Bench::log('ready', scenario: 'list');
    }

    private static function compact(int $i): Element
    {
        return Column::make(
            Text::make("Item {$i}")->style(Bench::text(16, weight: 700)),
            Text::make("Subtitle for item {$i}")->style(Bench::text(13, Bench::MUTED)),
        )->style(new Style(height: 64, paddingHorizontal: 16, justifyContent: Justify::Center));
    }

    private static function avatar(int $i): Element
    {
        return Row::make(
            View::make(
                Text::make('I'.($i % 10))->style(Bench::text(16, 0xFFFFFFFF, 700)),
            )->style(new Style(
                width: 48,
                height: 48,
                borderRadius: 24,
                backgroundColor: Bench::PALETTE[$i % 8],
                alignItems: Align::Center,
                justifyContent: Justify::Center,
            )),
            Column::make(
                Text::make("Item {$i}")->style(Bench::text(16, weight: 700)),
                Text::make("Subtitle for item {$i}")->style(Bench::text(13, Bench::MUTED)),
            )->style(new Style(flexGrow: 1, flexShrink: 1)),
            Text::make((string) ($i % 100))->style(new Style(
                paddingHorizontal: 10,
                paddingVertical: 2,
                backgroundColor: 0xFFEEF2FF,
                textColor: Bench::TEXT,
                fontSize: 13,
                borderRadius: 999,
            )),
        )->style(new Style(height: 72, paddingHorizontal: 16, gap: 12, alignItems: Align::Center));
    }

    private static function card(int $i): Element
    {
        $lcg = new Lcg(42 + $i);
        $sentences = [];
        for ($k = ($i % 4) + 1; $k > 0; $k--) {
            $words = [];
            for ($w = 0; $w < 8; $w++) {
                $words[] = $lcg->word();
            }
            $sentences[] = ucfirst(implode(' ', $words)).'.';
        }

        return Column::make(
            Text::make("Card {$i}")->style(Bench::text(16, weight: 700)),
            Text::make(implode(' ', $sentences))->style(Bench::text(14)),
        )->style(new Style(
            padding: 16,
            gap: 4,
            marginHorizontal: 16,
            marginVertical: 8,
            borderRadius: 12,
            backgroundColor: 0xFFF3F4F6,
        ));
    }
}
