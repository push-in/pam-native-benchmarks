<?php

declare(strict_types=1);

namespace App\Compute;

use App\Support\Bench;
use App\Support\Lcg;
use Closure;

/**
 * The `compute` workloads in plain, idiomatic PHP. Inputs are prepared
 * outside the timed region; each operation is timed 5 times (median).
 */
final class ComputeSuite
{
    private const int RUNS = 5;
    private const int DOCS = 100_000;
    private const int RECORDS = 100_000;

    /** @var list<string> */
    private array $docs = [];

    /** @var list<string> */
    private array $index = [];

    /** @var list<array{name: string, n: int}> */
    private array $records = [];

    /** @var list<array{id: int, v: int}> */
    private array $before = [];

    /** @var list<array{id: int, v: int}> */
    private array $after = [];

    private string $buffer = '';

    private mixed $decoded = null;

    public function __construct(private readonly string $json)
    {
    }

    /** @return list<Closure(): array{string, float, string}> one step per operation */
    public function steps(): array
    {
        return [
            fn () => $this->measure('search_build', $this->prepareDocs(...), function (): string {
                $this->index = array_map(strtolower(...), $this->docs);

                return (string) count($this->index);
            }),
            fn () => $this->measure('search_query', null, function (): string {
                $hits = 0;
                for ($q = 0; $q < 100; $q++) {
                    $first = Bench::WORDS[$q % 64];
                    $second = Bench::WORDS[($q * 7 + 3) % 64];
                    foreach ($this->index as $doc) {
                        if (str_contains($doc, $first) && str_contains($doc, $second)) {
                            $hits++;
                        }
                    }
                }

                return (string) $hits;
            }),
            fn () => $this->measure('json_parse', null, function (): string {
                $this->decoded = json_decode($this->json, true, flags: JSON_THROW_ON_ERROR);

                return (string) count($this->decoded);
            }),
            fn () => $this->measure('json_stringify', null, fn (): string => (string) strlen(
                json_encode($this->decoded, JSON_THROW_ON_ERROR | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE),
            )),
            fn () => $this->measure('sort', $this->prepareRecords(...), function (): string {
                $sorted = $this->records;
                usort($sorted, static fn (array $a, array $b): int => strcmp($a['name'], $b['name']) ?: $a['n'] <=> $b['n']);

                return (string) $sorted[0]['n'];
            }),
            fn () => $this->measure('sha256', $this->prepareBuffer(...), fn (): string => substr(hash('sha256', $this->buffer), 0, 8)),
            fn () => $this->measure('diff', $this->prepareLists(...), function (): string {
                $before = array_column($this->before, 'v', 'id');
                $after = array_column($this->after, 'v', 'id');
                $inserted = count(array_diff_key($after, $before));
                $removed = count(array_diff_key($before, $after));
                $changed = 0;
                foreach (array_intersect_key($after, $before) as $id => $value) {
                    if ($before[$id] !== $value) {
                        $changed++;
                    }
                }

                return "{$inserted}/{$removed}/{$changed}";
            }),
        ];
    }

    /**
     * @param null|Closure(): void $prepare untimed setup
     * @param Closure(): string $operation
     * @return array{string, float, string}
     */
    private function measure(string $name, ?Closure $prepare, Closure $operation): array
    {
        $prepare?->__invoke();
        $samples = [];
        $check = '';
        for ($run = 0; $run < self::RUNS; $run++) {
            $started = hrtime(true);
            $check = $operation();
            $samples[] = (hrtime(true) - $started) / 1_000_000;
        }
        sort($samples);

        return [$name, $samples[intdiv(self::RUNS, 2)], $check];
    }

    private function prepareDocs(): void
    {
        $lcg = new Lcg(42);
        for ($d = 0; $d < self::DOCS; $d++) {
            $words = [];
            for ($w = 0; $w < 8; $w++) {
                $words[] = $lcg->word();
            }
            $this->docs[] = implode(' ', $words);
        }
    }

    private function prepareRecords(): void
    {
        $this->docs = [];
        $this->index = [];
        $lcg = new Lcg(42);
        for ($i = 0; $i < self::RECORDS; $i++) {
            $name = $lcg->word().' '.$lcg->word();
            $this->records[] = ['name' => $name, 'n' => $lcg->next() % 100_000];
        }
    }

    private function prepareBuffer(): void
    {
        $this->decoded = null;
        $this->records = [];
        $this->buffer = str_repeat(implode('', array_map(chr(...), range(0, 255))), 10 * 1024 * 1024 / 256);
    }

    private function prepareLists(): void
    {
        $this->buffer = '';
        for ($i = 0; $i < 100_000; $i++) {
            $this->before[] = ['id' => $i, 'v' => $i];
            if ($i % 250 === 0) {
                continue;
            }
            $this->after[] = ['id' => $i, 'v' => $i % 100 === 0 ? $i + 1 : $i];
        }
        for ($id = 100_000; $id < 100_400; $id++) {
            $this->after[] = ['id' => $id, 'v' => $id];
        }
    }
}
