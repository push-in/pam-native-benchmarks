package dev.bench.nativeapp

import android.os.Bundle
import android.view.View
import android.widget.TextView
import androidx.core.view.doOnPreDraw
import androidx.fragment.app.Fragment
import okhttp3.Request
import org.json.JSONArray
import java.security.MessageDigest
import java.util.Locale

/**
 * Runs the compute ops on a background thread after the first frame.
 * JSON uses the platform org.json (the idiomatic zero-dependency Android API).
 */
class ComputeFragment : Fragment(R.layout.fragment_text) {
    private var worker: Thread? = null

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        val text = view as TextView
        text.text = "Computing…"
        logReadyAfterDraw(view, "ready scenario=compute")
        val http = Bench.http(requireContext())
        // Start only after the first frame is on screen.
        view.doOnPreDraw { view.post {
            if (this.view == null) return@post
            worker = Thread({
                try {
                    runAll { http.newCall(Request.Builder().url("${Bench.HOST}/compute.json").build()).execute().use { it.body!!.string() } }
                    Bench.log("compute done")
                    text.post { text.text = "Done" }
                } catch (e: InterruptedException) {
                    // Screen left; stop quietly.
                }
            }, "bench-compute").apply { start() }
        } }
    }

    override fun onDestroyView() {
        worker?.interrupt()
        worker = null
        super.onDestroyView()
    }

    private fun <T> measure(op: String, block: () -> T, check: (T) -> String) {
        val times = DoubleArray(RUNS)
        var result: T? = null
        for (r in 0 until RUNS) {
            if (Thread.interrupted()) throw InterruptedException()
            val start = System.nanoTime()
            result = block()
            times[r] = (System.nanoTime() - start) / 1_000_000.0
        }
        times.sort()
        val median = String.format(Locale.US, "%.3f", times[RUNS / 2])
        @Suppress("UNCHECKED_CAST")
        Bench.log("compute op=$op ms=$median check=${check(result as T)}")
    }

    private fun runAll(download: () -> String) {
        val words = Bench.WORDS

        // search_build: 100,000 docs of 8 words, one LCG stream seed 42.
        var docs: List<String> = emptyList()
        measure("search_build", {
            val lcg = Lcg(42)
            List(100_000) { buildString {
                repeat(8) { w -> if (w > 0) append(' '); append(lcg.word()) }
            }.lowercase() }.also { docs = it }
        }) { it.size.toString() }

        // search_query: 100 two-word AND queries, case-insensitive substring.
        measure("search_query", {
            var hits = 0
            for (q in 0 until 100) {
                val a = words[q % 64].lowercase()
                val b = words[(q * 7 + 3) % 64].lowercase()
                hits += docs.filter { it.contains(a) && it.contains(b) }.size
            }
            hits
        }) { it.toString() }
        docs = emptyList()

        // json_parse / json_stringify of /compute.json (downloaded once, not timed).
        val json = download()
        var parsed = JSONArray()
        measure("json_parse", { JSONArray(json).also { parsed = it } }) { it.length().toString() }
        measure("json_stringify", { parsed.toString() }) { it.toByteArray(Charsets.UTF_8).size.toString() }
        parsed = JSONArray()

        // sort: 100,000 {name, n} by name then n.
        data class Rec(val name: String, val n: Int)
        val lcg = Lcg(42)
        val records = List(100_000) {
            Rec("${lcg.word()} ${lcg.word()}", (lcg.next() % 100_000).toInt())
        }
        val byNameThenN = compareBy<Rec>({ it.name }, { it.n })
        measure("sort", { records.sortedWith(byNameThenN) }) { it.first().n.toString() }

        // sha256 of 10 MiB filled with i & 0xFF.
        val buffer = ByteArray(10 * 1024 * 1024) { (it and 0xFF).toByte() }
        measure("sha256", { MessageDigest.getInstance("SHA-256").digest(buffer) }) { digest ->
            digest.take(4).joinToString("") { String.format(Locale.US, "%02x", it) }
        }

        // diff: keyed lists A and B.
        val a = List(100_000) { Item(it, it) }
        val b = ArrayList<Item>(100_000)
        for (item in a) {
            if (item.id % 250 == 0) continue
            b += if (item.id % 100 == 0) Item(item.id, item.v + 1) else item
        }
        for (k in 0 until 400) b += Item(100_000 + k, 100_000 + k)
        measure("diff", { diff(a, b) }) { "${it[0]}/${it[1]}/${it[2]}" }
    }

    private data class Item(val id: Int, val v: Int)

    private fun diff(a: List<Item>, b: List<Item>): IntArray {
        val old = HashMap<Int, Int>(a.size * 2)
        for (item in a) old[item.id] = item.v
        var inserted = 0
        var changed = 0
        var kept = 0
        for (item in b) {
            val v = old[item.id]
            if (v == null) inserted++ else {
                kept++
                if (v != item.v) changed++
            }
        }
        return intArrayOf(inserted, a.size - kept, changed)
    }

    private companion object {
        const val RUNS = 5
    }
}
