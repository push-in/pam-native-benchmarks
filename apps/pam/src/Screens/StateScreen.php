<?php

declare(strict_types=1);

namespace App\Screens;

use App\Support\Bench;
use App\Support\Page;
use Pam\Native\Component;
use Pam\Native\Element;
use Pam\Native\Style;
use Pam\Native\UI\Text;

/** Holds N plain records in screen state (PSS at N=0 vs N=100000). */
final class StateScreen extends Component
{
    /** @var list<array{id: int, name: string, email: string, age: int, score: float, tags: list<string>}> */
    private array $records = [];

    public function __construct(private readonly int $n)
    {
    }

    public function boot(): void
    {
        for ($i = 0; $i < $this->n; $i++) {
            $this->records[] = [
                'id' => $i,
                'name' => "User {$i}",
                'email' => "user{$i}@example.com",
                'age' => $i % 90,
                'score' => $i * 0.5,
                'tags' => ['t'.($i % 7), 't'.($i % 11), 't'.($i % 13)],
            ];
        }
    }

    public function render(): Element
    {
        return Page::make(
            Text::make(count($this->records).' records')->style(new Style(padding: 16, textColor: Bench::TEXT, fontSize: 18)),
        );
    }

    public function attached(): void
    {
        Bench::log('ready', scenario: 'state', n: $this->n);
    }
}
