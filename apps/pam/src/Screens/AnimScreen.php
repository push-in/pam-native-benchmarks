<?php

declare(strict_types=1);

namespace App\Screens;

use App\Support\Bench;
use App\Support\Page;
use Pam\Native\Animation\Animation;
use Pam\Native\Animation\Easing;
use Pam\Native\Component;
use Pam\Native\Element;
use Pam\Native\Style;
use Pam\Native\UI\View;

/**
 * A square rotating 360°/1000 ms (linear) while sliding 0→150→0 dp per
 * 2000 ms (ease-in-out). One UI-thread motion program, repeated forever;
 * PHP describes it once and never runs per frame.
 */
final class AnimScreen extends Component
{
    public function render(): Element
    {
        $motion = Animation::sequence(
            Animation::timing(['rotate' => 360], 1000, Easing::Linear),
            Animation::timing(['rotate' => 720], 1000, Easing::Linear),
        )->with(Animation::sequence(
            Animation::timing(['translateX' => 150], 1000, Easing::EaseInOut),
            Animation::timing(['translateX' => 0], 1000, Easing::EaseInOut),
        ))->repeat(-1);

        return Page::make(
            View::make()
                ->animation($motion)
                ->style(new Style(width: 100, height: 100, margin: 16, backgroundColor: 0xFF3B82F6)),
        );
    }

    public function attached(): void
    {
        Bench::log('ready', scenario: 'anim');
    }
}
