<?php

declare(strict_types=1);

namespace App\Screens;

use App\Support\Bench;
use App\Support\Lcg;
use App\Support\Page;
use Pam\Native\Component;
use Pam\Native\Element;
use Pam\Native\InputAutoCapitalize;
use Pam\Native\InputSyncMode;
use Pam\Native\Justify;
use Pam\Native\Style;
use Pam\Native\UI\Text;
use Pam\Native\UI\TextInput;
use Pam\Native\UI\VirtualizedList;

/** Synchronous case-insensitive substring filter over 10,000 rows. */
final class FilterScreen extends Component
{
    private const int COUNT = 10_000;

    private string $query = '';

    /** @var list<string> lowercase search keys, by row index */
    private array $keys = [];

    /** @var list<Element> immutable row elements, built once */
    private array $rows = [];

    /** @var list<string> row labels, by row index */
    private array $labels = [];

    public function boot(): void
    {
        $lcg = new Lcg(42);
        $eager = !method_exists(VirtualizedList::class, 'of');
        for ($i = 0; $i < self::COUNT; $i++) {
            $label = "Name {$i} ".$lcg->word();
            $this->keys[] = strtolower($label);
            $this->labels[] = $label;
            if ($eager) {
                $this->rows[] = $this->rowAt($i)->key((string) $i);
            }
        }
    }

    private function rowAt(int $i): Element
    {
        return Text::make($this->labels[$i])
            ->style(new Style(
                height: 48,
                paddingHorizontal: 16,
                justifyContent: Justify::Center,
                textColor: Bench::TEXT,
                fontSize: 16,
            ));
    }

    public function render(): Element
    {
        $needle = strtolower($this->query);
        if (method_exists(VirtualizedList::class, 'of')) {
            return $this->page($needle);
        }
        $visible = $needle === ''
            ? $this->rows
            : array_values(array_filter(
                $this->rows,
                fn (int $i): bool => str_contains($this->keys[$i], $needle),
                ARRAY_FILTER_USE_KEY,
            ));

        return Page::make(
            TextInput::make($this->query)
                ->placeholder('Filter')
                ->caretHidden()
                // Same field as the RN (autoCorrect={false} autoCapitalize="none")
                // and native (textNoSuggestions) apps: no IME composing delay.
                ->autoCorrect(false)
                ->autoCapitalize(InputAutoCapitalize::None)
                ->nativeState(InputSyncMode::Immediate)
                ->onChange($this->search(...))
                ->accessibilityLabel('filter-input')
                ->style(new Style(
                    height: 48,
                    marginHorizontal: 16,
                    marginTop: 8,
                    paddingHorizontal: 12,
                    borderWidth: 1,
                    borderColor: 0xFFD1D5DB,
                    borderRadius: 8,
                    textColor: Bench::TEXT,
                    fontSize: 16,
                )),
            Text::make(count($visible).' results')
                ->style(new Style(paddingHorizontal: 16, paddingVertical: 8, textColor: Bench::MUTED, fontSize: 14)),
            VirtualizedList::make(...$visible)
                ->estimatedRowHeight(48)
                ->style(new Style(flexGrow: 1)),
        );
    }

    /** Data-driven rows (PAM Native 1.45+): only the shown rows are built. */
    private function page(string $needle): Element
    {
        $matches = $needle === ''
            ? array_keys($this->keys)
            : array_keys(array_filter($this->keys, static fn (string $key): bool => str_contains($key, $needle)));

        return Page::make(
            TextInput::make($this->query)
                ->placeholder('Filter')
                ->caretHidden()
                // Same field as the RN (autoCorrect={false} autoCapitalize="none")
                // and native (textNoSuggestions) apps: no IME composing delay.
                ->autoCorrect(false)
                ->autoCapitalize(InputAutoCapitalize::None)
                ->nativeState(InputSyncMode::Immediate)
                ->onChange($this->search(...))
                ->accessibilityLabel('filter-input')
                ->style(new Style(
                    height: 48,
                    marginHorizontal: 16,
                    marginTop: 8,
                    paddingHorizontal: 12,
                    borderWidth: 1,
                    borderColor: 0xFFD1D5DB,
                    borderRadius: 8,
                    textColor: Bench::TEXT,
                    fontSize: 16,
                )),
            Text::make(count($matches).' results')
                ->style(new Style(paddingHorizontal: 16, paddingVertical: 8, textColor: Bench::MUTED, fontSize: 14)),
            VirtualizedList::of($matches, fn (int $i): Element => $this->rowAt($i), static fn (int $i): int => $i)
                ->estimatedRowHeight(48)
                ->style(new Style(flexGrow: 1)),
        );
    }


    public function attached(): void
    {
        Bench::log('ready', scenario: 'filter');
    }

    public function search(string $value): void
    {
        $this->query = $value;
    }
}
