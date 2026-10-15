<?php

declare(strict_types=1);

namespace App\Templates;

use App\Support\Bench;
use App\Support\Lcg;
use Pam\Native\Component;

/** Synchronous substring filter over 10,000 rows, written as a template p-for. */
final class FilterPage extends Component
{
    public string $query = '';

    /** @var list<string> */
    public array $labels = [];

    /** @var list<int> row indexes matching the query */
    public array $visible = [];

    /** @var list<string> lowercase search keys */
    private array $keys = [];

    public function boot(): void
    {
        $lcg = new Lcg(42);
        for ($i = 0; $i < 10_000; $i++) {
            $label = "Name {$i} ".$lcg->word();
            $this->labels[] = $label;
            $this->keys[] = strtolower($label);
        }
        $this->visible = array_keys($this->keys);
    }

    public function attached(): void
    {
        Bench::log('ready', scenario: 'filter');
    }

    public function search(string $value): void
    {
        $this->query = $value;
        $needle = strtolower($value);
        $this->visible = $needle === ''
            ? array_keys($this->keys)
            : array_keys(array_filter($this->keys, static fn (string $key): bool => str_contains($key, $needle)));
    }
}
?>

<template>
    <Screen class="page">
        <SafeAreaView class="page">
            <Column class="grow">
                <Input
                    :value="$query"
                    sync="immediate"
                    placeholder="Filter"
                    caretHidden="true"
                    autoCorrect="false"
                    autoCapitalize="none"
                    accessibilityLabel="filter-input"
                    class="field"
                    on:change="search($event)"
                />
                <Text class="count">{{ count($visible) }} results</Text>
                <VirtualizedList estimatedRowHeight="48" class="grow">
                    <Text p-for="$i in $visible" :key="$i" class="row">{{ $labels[$i] }}</Text>
                </VirtualizedList>
            </Column>
        </SafeAreaView>
    </Screen>
</template>

<style scoped>
    .page { flex-grow: 1; background-color: #FFFFFF; }
    .grow { flex-grow: 1; }
    .field { height: 48px; margin: 8px 16px 0 16px; padding: 0 12px; border: 1px solid #D1D5DB; border-radius: 8px; color: #111827; font-size: 16px; }
    .count { padding: 8px 16px; color: #6B7280; font-size: 14px; }
    .row { height: 48px; padding: 0 16px; justify-content: center; color: #111827; font-size: 16px; }
</style>
