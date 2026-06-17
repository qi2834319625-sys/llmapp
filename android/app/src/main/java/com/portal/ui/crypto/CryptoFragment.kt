package com.portal.ui.crypto

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.*
import androidx.appcompat.app.AlertDialog
import androidx.fragment.app.Fragment
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.chip.Chip
import com.google.android.material.snackbar.Snackbar
import com.portal.PortalApp
import com.portal.R
import com.portal.data.model.CryptoPaper
import com.portal.data.repository.Resource
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch

class CryptoFragment : Fragment() {

    private var allPapers: List<CryptoPaper> = emptyList()

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View? {
        return inflater.inflate(R.layout.fragment_crypto, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val toolbar = view.findViewById<androidx.appcompat.widget.Toolbar>(R.id.toolbar)
        val swipeRefresh = view.findViewById<androidx.swiperefreshlayout.widget.SwipeRefreshLayout>(R.id.swipe_refresh)
        val recyclerView = view.findViewById<RecyclerView>(R.id.rv_crypto)
        recyclerView?.layoutManager = LinearLayoutManager(requireContext())

        // Toolbar menu
        toolbar?.inflateMenu(R.menu.menu_crypto)
        toolbar?.setOnMenuItemClickListener { menuItem ->
            when (menuItem.itemId) {
                R.id.action_search -> {
                    // Simple search dialog
                    val editText = EditText(requireContext()).apply { hint = "搜索论文..." }
                    AlertDialog.Builder(requireContext())
                        .setTitle("搜索")
                        .setView(editText)
                        .setPositiveButton("搜索") { _, _ ->
                            val query = editText.text.toString().trim()
                            loadPapers(if (query.isEmpty()) "" else query, "")
                        }
                        .setNegativeButton("取消", null)
                        .show()
                    true
                }
                R.id.action_filter -> {
                    showFilterDialog()
                    true
                }
                else -> false
            }
        }

        swipeRefresh?.setOnRefreshListener { loadPapers("", "") }
        loadPapers("", "")
    }

    private fun loadPapers(search: String, category: String) {
        view?.findViewById<androidx.swiperefreshlayout.widget.SwipeRefreshLayout>(R.id.swipe_refresh)?.isRefreshing = true
        GlobalScope.launch {
            PortalApp.instance.repository.getCryptoPapers(1940, 2026, category, search)
                .observe(viewLifecycleOwner) { resource ->
                    view?.findViewById<androidx.swiperefreshlayout.widget.SwipeRefreshLayout>(R.id.swipe_refresh)?.isRefreshing = false
                    when (resource) {
                        is Resource.Success -> {
                            allPapers = resource.data.papers
                            view?.findViewById<RecyclerView>(R.id.rv_crypto)?.adapter = PaperAdapter(allPapers)
                        }
                        is Resource.Error -> {
                            view?.post { Snackbar.make(requireView(), "加载失败: ${resource.message}", Snackbar.LENGTH_SHORT).show() }
                        }
                        is Resource.Loading -> {}
                    }
                }
        }
    }

    private fun showFilterDialog() {
        val categories = listOf("All", "Encryption", "Signature", "Protocol", "Hash", "Zero-Knowledge", "MPC", "Blockchain")
        val chipGroup = com.google.android.material.chip.ChipGroup(requireContext())
        categories.forEach { cat ->
            val chip = Chip(requireContext()).apply {
                text = cat
                isCheckable = true
                isChecked = cat == "All"
            }
            chipGroup.addView(chip)
        }

        AlertDialog.Builder(requireContext())
            .setTitle("选择类别")
            .setView(chipGroup)
            .setPositiveButton("确定") { _, _ ->
                val selected = (0 until chipGroup.childCount)
                    .map { chipGroup.getChildAt(it) as? Chip }
                    .firstOrNull { it?.isChecked == true }
                    ?.text?.toString() ?: "All"
                loadPapers("", if (selected == "All") "" else selected)
            }
            .setNegativeButton("取消", null)
            .show()
    }

    class PaperAdapter(private val papers: List<CryptoPaper>) : RecyclerView.Adapter<PaperAdapter.VH>() {

        class VH(view: View) : RecyclerView.ViewHolder(view) {
            val title: TextView = view.findViewById(R.id.tv_title)
            val authors: TextView = view.findViewById(R.id.tv_authors)
            val year: Chip = view.findViewById(R.id.chip_year)
            val category: Chip = view.findViewById(R.id.chip_category)
            val abstract: TextView = view.findViewById(R.id.tv_abstract)
        }

        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
            val view = LayoutInflater.from(parent.context).inflate(R.layout.item_paper, parent, false)
            return VH(view)
        }

        override fun onBindViewHolder(holder: VH, position: Int) {
            val paper = papers[position]
            holder.title.text = paper.title
            holder.authors.text = paper.authors
            holder.year.text = paper.year.toString()
            holder.category.text = paper.category
            holder.abstract.text = paper.abstract.take(150)

            // Expand/collapse on click
            holder.itemView.setOnClickListener {
                if (holder.abstract.maxLines == 3) {
                    holder.abstract.maxLines = Int.MAX_VALUE
                } else {
                    holder.abstract.maxLines = 3
                }
            }
        }

        override fun getItemCount() = papers.size
    }
}
