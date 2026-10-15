package dev.bench.nativeapp

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView

class ListFragment : Fragment(R.layout.fragment_recycler) {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        val list = view as RecyclerView
        list.layoutManager = LinearLayoutManager(requireContext())
        list.setHasFixedSize(true)
        list.adapter = BenchListAdapter()
        logReadyAfterDraw(list, "ready scenario=list")
    }
}

private class BenchListAdapter : RecyclerView.Adapter<BenchListAdapter.Holder>() {

    class Holder(view: View) : RecyclerView.ViewHolder(view) {
        val title: TextView = view.findViewById(R.id.title)
        val subtitle: TextView? = view.findViewById(R.id.subtitle)
        val avatar: TextView? = view.findViewById(R.id.avatar)
        val badge: TextView? = view.findViewById(R.id.badge)
        val body: TextView? = view.findViewById(R.id.body)
    }

    override fun getItemCount() = 10_000

    override fun getItemViewType(position: Int) = position % 3

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): Holder {
        val layout = when (viewType) {
            0 -> R.layout.item_compact
            1 -> R.layout.item_avatar
            else -> R.layout.item_card
        }
        val view = LayoutInflater.from(parent.context).inflate(layout, parent, false)
        return Holder(view).also { holder ->
            // Each avatar owns its drawable so the per-row tint does not leak to others.
            holder.avatar?.background?.mutate()
        }
    }

    override fun onBindViewHolder(holder: Holder, position: Int) {
        when (position % 3) {
            0 -> {
                holder.title.text = "Item $position"
                holder.subtitle!!.text = "Subtitle for item $position"
            }
            1 -> {
                holder.title.text = "Item $position"
                holder.subtitle!!.text = "Subtitle for item $position"
                val avatar = holder.avatar!!
                avatar.background.setTint(Bench.PALETTE[position % 8])
                avatar.text = "I${position % 10}"
                holder.badge!!.text = (position % 100).toString()
            }
            else -> {
                holder.title.text = "Card $position"
                holder.body!!.text = cardBody(position)
            }
        }
    }

    private fun cardBody(i: Int): String {
        val lcg = Lcg(42L + i)
        val sb = StringBuilder()
        repeat(i % 4 + 1) { s ->
            if (s > 0) sb.append(' ')
            repeat(8) { w ->
                val word = lcg.word()
                if (w == 0) {
                    sb.append(word[0].uppercaseChar()).append(word, 1, word.length)
                } else {
                    sb.append(' ').append(word)
                }
            }
            sb.append('.')
        }
        return sb.toString()
    }
}
