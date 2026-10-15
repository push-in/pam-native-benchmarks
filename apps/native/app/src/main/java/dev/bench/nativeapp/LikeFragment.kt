package dev.bench.nativeapp

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.core.content.ContextCompat
import androidx.core.view.doOnPreDraw
import androidx.fragment.app.Fragment
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import androidx.recyclerview.widget.SimpleItemAnimator

class LikeFragment : Fragment(R.layout.fragment_recycler) {
    /** Screen state: which rows are liked. */
    private val liked = BooleanArray(COUNT)
    private var bindsSinceLike = 0

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        val list = view as RecyclerView
        list.layoutManager = LinearLayoutManager(requireContext())
        list.setHasFixedSize(true)
        (list.itemAnimator as? SimpleItemAnimator)?.supportsChangeAnimations = false
        list.adapter = LikeAdapter()
        logReadyAfterDraw(list, "ready scenario=like")
    }

    private fun toggle(list: RecyclerView, i: Int) {
        liked[i] = !liked[i]
        Bench.log("like i=$i liked=${if (liked[i]) 1 else 0}")
        bindsSinceLike = 0
        list.adapter!!.notifyItemChanged(i, PAYLOAD_LIKE)
        list.doOnPreDraw { Bench.log("rerender count=$bindsSinceLike") }
    }

    private inner class LikeAdapter : RecyclerView.Adapter<LikeAdapter.Holder>() {
        private val likedBg = ContextCompat.getColor(requireContext(), R.color.liked)

        inner class Holder(view: View) : RecyclerView.ViewHolder(view) {
            val title: TextView = view.findViewById(R.id.title)
            val like: TextView = view.findViewById(R.id.like)
        }

        override fun getItemCount() = COUNT

        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): Holder {
            val view = LayoutInflater.from(parent.context).inflate(R.layout.item_like, parent, false)
            return Holder(view).also { holder ->
                holder.like.setOnClickListener {
                    val position = holder.bindingAdapterPosition
                    if (position != RecyclerView.NO_POSITION) toggle(parent as RecyclerView, position)
                }
            }
        }

        override fun onBindViewHolder(holder: Holder, position: Int) {
            holder.title.text = "Post $position"
            holder.like.contentDescription = "like-$position"
            bindLike(holder, position)
        }

        override fun onBindViewHolder(holder: Holder, position: Int, payloads: List<Any>) {
            if (payloads.contains(PAYLOAD_LIKE)) bindLike(holder, position)
            else onBindViewHolder(holder, position)
        }

        private fun bindLike(holder: Holder, i: Int) {
            bindsSinceLike++
            val likes = i * 7 % 50
            if (liked[i]) {
                holder.like.text = "♥ ${likes + 1}"
                holder.itemView.setBackgroundColor(likedBg)
            } else {
                holder.like.text = "♡ $likes"
                holder.itemView.background = null
            }
        }
    }

    private companion object {
        const val COUNT = 200
        const val PAYLOAD_LIKE = "like"
    }
}
