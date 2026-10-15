package dev.bench.nativeapp

import android.annotation.SuppressLint
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.EditText
import android.widget.TextView
import androidx.core.widget.doAfterTextChanged
import androidx.fragment.app.Fragment
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView

class FilterFragment : Fragment(R.layout.fragment_filter) {
    private val rows: Array<String>
    private val rowsLower: Array<String>
    private var visible: IntArray

    init {
        val lcg = Lcg(42)
        rows = Array(COUNT) { i -> "Name $i ${lcg.word()}" }
        rowsLower = Array(COUNT) { rows[it].lowercase() }
        visible = IntArray(COUNT) { it }
    }

    private val adapter = RowAdapter()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        val input = view.findViewById<EditText>(R.id.input)
        val count = view.findViewById<TextView>(R.id.count)
        val list = view.findViewById<RecyclerView>(R.id.list)
        input.isCursorVisible = false
        list.layoutManager = LinearLayoutManager(requireContext())
        list.setHasFixedSize(true)
        list.itemAnimator = null
        list.adapter = adapter
        count.text = "${visible.size} results"

        input.doAfterTextChanged { text ->
            applyFilter(text?.toString().orEmpty())
            count.text = "${visible.size} results"
        }
        logReadyAfterDraw(list, "ready scenario=filter")
    }

    @SuppressLint("NotifyDataSetChanged")
    private fun applyFilter(query: String) {
        val q = query.lowercase()
        visible = if (q.isEmpty()) {
            IntArray(COUNT) { it }
        } else {
            rowsLower.indices.filter { rowsLower[it].contains(q) }.toIntArray()
        }
        adapter.notifyDataSetChanged()
    }

    private inner class RowAdapter : RecyclerView.Adapter<RowAdapter.Holder>() {
        inner class Holder(val text: TextView) : RecyclerView.ViewHolder(text)

        override fun getItemCount() = visible.size

        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int) =
            Holder(LayoutInflater.from(parent.context).inflate(R.layout.item_filter, parent, false) as TextView)

        override fun onBindViewHolder(holder: Holder, position: Int) {
            holder.text.text = rows[visible[position]]
        }
    }

    private companion object {
        const val COUNT = 10_000
    }
}
