package dev.bench.nativeapp

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import coil3.load
import okhttp3.Call
import okhttp3.Callback
import okhttp3.Request
import okhttp3.Response
import org.json.JSONObject
import java.io.IOException

class FeedFragment : Fragment(R.layout.fragment_recycler) {
    private data class Post(val title: String, val body: String, val image: String)

    private var call: Call? = null
    private val adapter = FeedAdapter()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        val list = view as RecyclerView
        list.layoutManager = LinearLayoutManager(requireContext())
        list.setHasFixedSize(true)
        list.adapter = adapter
        load(list)
    }

    private fun load(list: RecyclerView) {
        val request = Request.Builder().url("${Bench.HOST}/feed.json").build()
        call = Bench.http(requireContext()).newCall(request).also {
            it.enqueue(object : Callback {
                override fun onFailure(call: Call, e: IOException) {
                    if (!call.isCanceled()) Bench.log("error scenario=feed message=${e.javaClass.simpleName}")
                }

                override fun onResponse(call: Call, response: Response) {
                    val (posts, source) = response.use { r ->
                        // Served from disk cache, or revalidated by a 304: no body crossed the network.
                        val network = r.networkResponse
                        val source = if (network == null || network.code == 304) "cache" else "network"
                        parse(r.body!!.string()) to source
                    }
                    list.post {
                        if (view == null) return@post
                        adapter.submit(posts)
                        logReadyAfterDraw(list, "ready scenario=feed source=$source")
                    }
                }
            })
        }
    }

    private fun parse(json: String): List<Post> {
        val array = JSONObject(json).getJSONArray("posts")
        return List(array.length()) { i ->
            val o = array.getJSONObject(i)
            Post(o.getString("title"), o.getString("body"), o.getString("image"))
        }
    }

    override fun onDestroyView() {
        call?.cancel()
        call = null
        super.onDestroyView()
    }

    private class FeedAdapter : RecyclerView.Adapter<FeedAdapter.Holder>() {
        private var posts: List<Post> = emptyList()

        class Holder(view: View) : RecyclerView.ViewHolder(view) {
            val image: ImageView = view.findViewById(R.id.image)
            val title: TextView = view.findViewById(R.id.title)
            val body: TextView = view.findViewById(R.id.body)
        }

        fun submit(items: List<Post>) {
            posts = items
            notifyItemRangeInserted(0, items.size)
        }

        override fun getItemCount() = posts.size

        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int) =
            Holder(LayoutInflater.from(parent.context).inflate(R.layout.item_feed, parent, false))

        override fun onBindViewHolder(holder: Holder, position: Int) {
            val post = posts[position]
            holder.image.load(post.image)
            holder.title.text = post.title
            holder.body.text = post.body
        }
    }
}
