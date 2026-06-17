package com.portal.ui.cetexam

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.*
import androidx.fragment.app.Fragment
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.chip.Chip
import com.google.android.material.chip.ChipGroup
import com.google.android.material.snackbar.Snackbar
import com.google.android.material.tabs.TabLayout
import com.portal.PortalApp
import com.portal.R
import com.portal.data.model.CetExamItem
import com.portal.data.repository.Resource
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch

class CetExamFragment : Fragment() {

    private var currentExamType = "CET-4"
    private var currentSection = ""

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View? {
        return inflater.inflate(R.layout.fragment_cet_exam, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val swipeRefresh = view.findViewById<androidx.swiperefreshlayout.widget.SwipeRefreshLayout>(R.id.swipe_refresh)
        val recyclerView = view.findViewById<RecyclerView>(R.id.rv_cet_exam)
        recyclerView?.layoutManager = LinearLayoutManager(requireContext())

        // CET-4 / CET-6 tabs
        val tabLayout = TabLayout(requireContext()).apply {
            id = View.generateViewId()
            val tab4 = newTab().setText("CET-4")
            val tab6 = newTab().setText("CET-6")
            addTab(tab4)
            addTab(tab6)
            addOnTabSelectedListener(object : TabLayout.OnTabSelectedListener {
                override fun onTabSelected(tab: TabLayout.Tab?) {
                    currentExamType = if (tab?.position == 0) "CET-4" else "CET-6"
                    loadItems()
                }
                override fun onTabUnselected(tab: TabLayout.Tab?) {}
                override fun onTabReselected(tab: TabLayout.Tab?) {}
            })
        }

        // Section filter chips
        val sectionGroup = ChipGroup(requireContext()).apply {
            id = View.generateViewId()
            setPadding(16, 8, 16, 8)
        }
        val sections = listOf("All", "Vocabulary", "Reading", "Listening", "Writing", "Translation")
        sections.forEach { section ->
            val chip = Chip(requireContext()).apply {
                text = section
                isCheckable = true
                isChecked = section == "All"
                setOnClickListener {
                    currentSection = if (section == "All") "" else section
                    loadItems()
                }
            }
            sectionGroup.addView(chip)
        }

        // Add to layout
        val rootLayout = view as? ViewGroup
        rootLayout?.addView(tabLayout, 0)
        rootLayout?.addView(sectionGroup, 1)

        swipeRefresh?.setOnRefreshListener { loadItems() }
        loadItems()
    }

    private fun loadItems() {
        view?.findViewById<androidx.swiperefreshlayout.widget.SwipeRefreshLayout>(R.id.swipe_refresh)?.isRefreshing = true
        GlobalScope.launch {
            PortalApp.instance.repository.getCetExam(currentExamType, currentSection, "").observe(viewLifecycleOwner) { resource ->
                view?.findViewById<androidx.swiperefreshlayout.widget.SwipeRefreshLayout>(R.id.swipe_refresh)?.isRefreshing = false
                when (resource) {
                    is Resource.Success -> {
                        view?.findViewById<RecyclerView>(R.id.rv_cet_exam)?.adapter = CetAdapter(resource.data.items)
                    }
                    is Resource.Error -> {
                        view?.post { Snackbar.make(requireView(), "加载失败: ${resource.message}", Snackbar.LENGTH_SHORT).show() }
                    }
                    is Resource.Loading -> {}
                }
            }
        }
    }

    class CetAdapter(private val items: List<CetExamItem>) : RecyclerView.Adapter<CetAdapter.VH>() {
        class VH(view: View) : RecyclerView.ViewHolder(view) {
            val section: Chip = view.findViewById(R.id.chip_section)
            val difficulty: Chip = view.findViewById(R.id.chip_difficulty)
            val title: TextView = view.findViewById(R.id.tv_title)
            val content: TextView = view.findViewById(R.id.tv_content)
        }
        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
            val view = LayoutInflater.from(parent.context).inflate(R.layout.item_cet_exam, parent, false)
            return VH(view)
        }
        override fun onBindViewHolder(holder: VH, position: Int) {
            val item = items[position]
            holder.section.text = item.section
            holder.difficulty.text = item.difficulty
            holder.title.text = item.title
            holder.content.text = item.content.take(120)
        }
        override fun getItemCount() = items.size
    }
}
