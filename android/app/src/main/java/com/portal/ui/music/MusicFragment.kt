package com.portal.ui.music

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.*
import androidx.fragment.app.Fragment
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.snackbar.Snackbar
import com.portal.PortalApp
import com.portal.R
import com.portal.data.model.MusicTrack
import com.portal.data.repository.Resource
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch

class MusicFragment : Fragment() {

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View? {
        return inflater.inflate(R.layout.fragment_music, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val searchView = view.findViewById<SearchView>(R.id.search_view)
        val recyclerView = view.findViewById<RecyclerView>(R.id.rv_music)
        val progressBar = view.findViewById<ProgressBar>(R.id.progress_bar)

        recyclerView?.layoutManager = LinearLayoutManager(requireContext())

        searchView?.setOnQueryTextListener(object : SearchView.OnQueryTextListener {
            override fun onQueryTextSubmit(query: String?): Boolean {
                if (!query.isNullOrBlank()) {
                    progressBar?.visibility = View.VISIBLE
                    GlobalScope.launch {
                        PortalApp.instance.repository.searchMusic(query).observe(viewLifecycleOwner) { resource ->
                            progressBar?.visibility = View.GONE
                            when (resource) {
                                is Resource.Success -> {
                                    val tracks = resource.data.songs
                                    recyclerView?.adapter = MusicAdapter(tracks) { track ->
                                        track.previewUrl.takeIf { it.isNotEmpty() }?.let { url ->
                                            startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url)))
                                        }
                                    }
                                }
                                is Resource.Error -> {
                                    view?.post {
                                        Snackbar.make(requireView(), "搜索失败: ${resource.message}", Snackbar.LENGTH_SHORT).show()
                                    }
                                }
                                is Resource.Loading -> {}
                            }
                        }
                    }
                }
                return true
            }
            override fun onQueryTextChange(newText: String?) = false
        })
    }

    class MusicAdapter(
        private val tracks: List<MusicTrack>,
        private val onPlay: (MusicTrack) -> Unit
    ) : RecyclerView.Adapter<MusicAdapter.VH>() {

        class VH(view: View) : RecyclerView.ViewHolder(view) {
            val title: TextView = view.findViewById(R.id.tv_title)
            val singer: TextView = view.findViewById(R.id.tv_singer)
            val album: TextView = view.findViewById(R.id.tv_album)
            val duration: TextView = view.findViewById(R.id.tv_duration)
            val playBtn: ImageButton = view.findViewById(R.id.btn_play)
        }

        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
            val view = LayoutInflater.from(parent.context).inflate(R.layout.item_music, parent, false)
            return VH(view)
        }

        override fun onBindViewHolder(holder: VH, position: Int) {
            val track = tracks[position]
            holder.title.text = track.title
            holder.singer.text = track.singer
            holder.album.text = track.album
            holder.duration.text = formatInterval(track.interval)
            holder.playBtn.setOnClickListener { onPlay(track) }
        }

        override fun getItemCount() = tracks.size

        private fun formatInterval(seconds: Int): String {
            val m = seconds / 60
            val s = seconds % 60
            return "$m:${s.toString().padStart(2, '0')}"
        }
    }
}
