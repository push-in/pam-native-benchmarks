<?php

declare(strict_types=1);

namespace App\Screens;

use App\Support\Bench;
use App\Support\Page;
use Pam\Native\AccessibilityRole;
use Pam\Native\Align;
use Pam\Native\Component;
use Pam\Native\Element;
use Pam\Native\ImageFit;
use Pam\Native\Justify;
use Pam\Native\Style;
use Pam\Native\UI\Column;
use Pam\Native\UI\Image;
use Pam\Native\UI\ScrollView;
use Pam\Native\UI\Text;
use Pam\Native\UI\TouchableWithoutFeedback;

/** Stack screen `k`: pushes `k + 1`; system Back pops natively. */
final class NavScreen extends Component
{
    public function __construct(private readonly int $k)
    {
    }

    public function render(): Element
    {
        $rows = [];
        for ($j = 0; $j < 50; $j++) {
            $rows[] = Text::make("Row {$j}")
                ->key((string) $j)
                ->style(new Style(height: 40, paddingHorizontal: 16, textColor: Bench::TEXT, fontSize: 16));
        }

        return Page::make(
            Text::make("Screen {$this->k}")->style(new Style(padding: 16, textColor: Bench::TEXT, fontSize: 22, fontWeight: 700)),
            Image::make(Bench::ASSETS."/img/{$this->k}.jpg")
                ->fit(ImageFit::Cover)
                ->style(new Style(height: 200, widthPercent: 100)),
            TouchableWithoutFeedback::make(
                Text::make('next')->style(Bench::text(16, 0xFFFFFFFF, 700)),
            )
                ->accessibilityLabel('next')
                ->accessibilityRole(AccessibilityRole::Button)
                ->onPress(fn () => $this->pushRoute('nav', k: $this->k + 1))
                ->style(new Style(
                    height: 48,
                    margin: 16,
                    borderRadius: 8,
                    backgroundColor: 0xFF3B82F6,
                    alignItems: Align::Center,
                    justifyContent: Justify::Center,
                )),
            ScrollView::make(Column::make(...$rows))->style(new Style(flexGrow: 1, flexShrink: 1)),
        )->onRouteFocused($this->shown(...));
    }

    public function attached(): void
    {
        $this->shown();
    }

    public function shown(): void
    {
        Bench::log('ready', scenario: 'nav', k: $this->k);
    }
}
