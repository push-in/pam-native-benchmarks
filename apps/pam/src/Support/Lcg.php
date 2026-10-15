<?php

declare(strict_types=1);

namespace App\Support;

/** `x = (x * 1103515245 + 12345) mod 2^31`; next() returns the value after one step. */
final class Lcg
{
    public function __construct(private int $x)
    {
    }

    public function next(): int
    {
        return $this->x = ($this->x * 1103515245 + 12345) & 0x7FFFFFFF;
    }

    public function word(): string
    {
        return Bench::WORDS[$this->next() % 64];
    }
}
