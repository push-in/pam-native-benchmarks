<?php

declare(strict_types=1);

namespace App\Screens;

use App\Support\Bench;
use App\Support\Page;
use Pam\Native\Component;
use Pam\Native\Element;
use Pam\Native\Navigation\Navigator;
use Pam\Native\Style;
use Pam\Native\UI\Column;
use Pam\Native\UI\Text;

/** Static screen; also routes the cold-start `bench://` URI. */
final class HomeScreen extends Component
{
    public function __construct(private readonly ?Navigator $navigator)
    {
    }

    public function render(): Element
    {
        return Page::make(
            Column::make(
                Text::make('Bench')->style(Bench::text(28, weight: 700)),
                Text::make('Line 1')->style(Bench::text(16)),
                Text::make('Line 2')->style(Bench::text(16)),
                Text::make('Line 3')->style(Bench::text(16)),
            )->style(new Style(padding: 16, gap: 8)),
        );
    }

    public function attached(): void
    {
        Bench::log('ready', scenario: 'home');
    }
}
