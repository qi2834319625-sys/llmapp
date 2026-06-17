package com.portal.ui.more

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.*
import androidx.fragment.app.Fragment
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.portal.R
import com.portal.ui.cooking.CookingFragment
import com.portal.ui.fashion.FashionFragment
import com.portal.ui.investment.InvestmentFragment
import com.portal.ui.manga.MangaFragment
import com.portal.ui.makeup.MakeupFragment
import com.portal.ui.music.MusicFragment
import com.portal.ui.settings.SettingsFragment
import com.portal.ui.studyabroad.StudyAbroadFragment

class MoreFragment : Fragment() {

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View? {
        return inflater.inflate(R.layout.fragment_more, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val recyclerView = view.findViewById<RecyclerView>(R.id.rv_more)
        recyclerView?.layoutManager = LinearLayoutManager(requireContext())

        val modules = listOf(
            MoreItem("📈", "投资理财") { InvestmentFragment() },
            MoreItem("💄", "美妆系统") { MakeupFragment() },
            MoreItem("👗", "服装搭配") { FashionFragment() },
            MoreItem("🍳", "美食厨房") { CookingFragment() },
            MoreItem("✈️", "出国规划") { StudyAbroadFragment() },
            MoreItem("🎭", "漫剧创作") { MangaFragment() },
            MoreItem("🎵", "音乐搜索") { MusicFragment() },
            MoreItem("⚙️", "系统设置") { SettingsFragment() }
        )

        recyclerView?.adapter = MoreAdapter(modules) { fragment ->
            requireActivity().supportFragmentManager.beginTransaction()
                .replace(R.id.nav_host_fragment, fragment)
                .addToBackStack(null)
                .commit()
        }
    }

    data class MoreItem(val icon: String, val name: String, val fragment: () -> Fragment)

    class MoreAdapter(
        private val items: List<MoreItem>,
        private val onClick: (Fragment) -> Unit
    ) : RecyclerView.Adapter<MoreAdapter.VH>() {

        class VH(view: View) : RecyclerView.ViewHolder(view) {
            val icon: TextView = view.findViewById(R.id.tv_icon)
            val name: TextView = view.findViewById(R.id.tv_name)
        }

        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
            val view = LayoutInflater.from(parent.context).inflate(R.layout.item_more, parent, false)
            return VH(view)
        }

        override fun onBindViewHolder(holder: VH, position: Int) {
            val item = items[position]
            holder.icon.text = item.icon
            holder.name.text = item.name
            holder.itemView.setOnClickListener { onClick(item.fragment()) }
        }

        override fun getItemCount() = items.size
    }
}
