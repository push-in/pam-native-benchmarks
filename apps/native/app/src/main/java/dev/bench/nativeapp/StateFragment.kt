package dev.bench.nativeapp

import android.os.Bundle
import android.view.View
import android.widget.TextView
import androidx.fragment.app.Fragment

class StateFragment : Fragment(R.layout.fragment_text) {
    data class UserRecord(
        val id: Int,
        val name: String,
        val email: String,
        val age: Int,
        val score: Double,
        val tags: List<String>,
    )

    /** Screen state kept referenced for the lifetime of the screen. */
    private var records: List<UserRecord> = emptyList()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val n = requireArguments().getInt(ARG_N)
        records = List(n) { i ->
            UserRecord(
                id = i,
                name = "User $i",
                email = "user$i@example.com",
                age = i % 90,
                score = i * 0.5,
                tags = listOf("t${i % 7}", "t${i % 11}", "t${i % 13}"),
            )
        }
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        (view as TextView).text = "${records.size} records"
        logReadyAfterDraw(view, "ready scenario=state n=${records.size}")
    }

    companion object {
        private const val ARG_N = "n"

        fun newInstance(n: Int) = StateFragment().apply {
            arguments = Bundle().apply { putInt(ARG_N, n) }
        }
    }
}
