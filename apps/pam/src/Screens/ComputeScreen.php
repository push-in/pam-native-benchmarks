<?php

declare(strict_types=1);

namespace App\Screens;

use App\Compute\ComputeSuite;
use App\Support\Bench;
use App\Support\Page;
use Closure;
use Pam\Native\Component;
use Pam\Native\Element;
use Pam\Native\Http\Http;
use Pam\Native\Http\HttpResponse;
use Pam\Native\Style;
use Pam\Native\UI\Text;
use RuntimeException;

/**
 * Downloads `/compute.json` once (untimed), then runs one workload per
 * timer tick so the PHP thread yields between operations.
 */
final class ComputeScreen extends Component
{
    /** The PAM HTTP bridge caps a response body at 900 KiB: fetch in ranges. */
    private const int CHUNK = 512 * 1024;

    private string $status = 'Compute';

    private string $body = '';

    public function render(): Element
    {
        return Page::make(
            Text::make($this->status)->style(new Style(padding: 16, textColor: Bench::TEXT, fontSize: 18)),
        );
    }

    public function attached(): void
    {
        // Runtime facts for the scoreboard (PAM only): is the PHP JIT active?
        $opcache = function_exists('opcache_get_status') ? (opcache_get_status(false) ?: []) : [];
        Bench::log(
            'runtime',
            php: PHP_VERSION,
            opcache: (int) ($opcache['opcache_enabled'] ?? 0),
            jit: (int) ($opcache['jit']['on'] ?? 0),
        );
        $this->download(0, function (string $json): void {
            $this->body = '';
            $this->run((new ComputeSuite($json))->steps());
        });
    }

    /** @param Closure(string): void $done */
    private function download(int $offset, Closure $done): void
    {
        $end = $offset + self::CHUNK - 1;
        Http::request(
            'GET',
            Bench::ASSETS.'/compute.json',
            function (HttpResponse $response) use ($offset, $done): void {
                if ($response->statusCode !== 206 && $response->statusCode !== 200) {
                    throw new RuntimeException("compute.json download failed: {$response->statusCode} {$response->error}");
                }
                $this->body .= $response->body;
                $total = (int) substr((string) strrchr($response->header('Content-Range') ?? '/0', '/'), 1);
                if ($response->statusCode === 206 && strlen($this->body) < $total) {
                    $this->download($offset + strlen($response->body), $done);

                    return;
                }
                $done($this->body);
            },
            headers: ['Range' => "bytes={$offset}-{$end}"],
            timeoutMs: 60_000,
        );
    }

    /** @param list<Closure(): array{string, float, string}> $steps */
    private function run(array $steps): void
    {
        if ($steps === []) {
            Bench::log('compute done');
            $this->status = 'Compute done';

            return;
        }
        $step = array_shift($steps);
        $this->timers()->timeout(0, function () use ($step, $steps): void {
            [$op, $ms, $check] = $step();
            Bench::log('compute', op: $op, ms: sprintf('%.3f', $ms), check: $check);
            $this->run($steps);
        });
    }
}
