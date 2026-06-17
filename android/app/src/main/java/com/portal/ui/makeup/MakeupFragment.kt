package com.portal.ui.makeup

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout
import com.google.android.material.chip.Chip
import com.google.android.material.chip.ChipGroup
import com.google.android.material.snackbar.Snackbar
import com.portal.PortalApp
import com.portal.R
import com.portal.data.model.MakeupTip
import com.portal.data.model.MakeupTipsResponse
import com.portal.data.repository.Resource

class MakeupFragment : Fragment() {

    private var rootView: View? = null
    private lateinit var adapter: MakeupTipAdapter
    private var allTips = listOf<MakeupTip>()
    private var selectedCategory = "All"
    private var categories = listOf<String>()

    private val chipGroupCategory: ChipGroup
        get() = rootView!!.findViewById(R.id.chip_group_category)
    private val recyclerView: RecyclerView
        get() = rootView!!.findViewById(R.id.rv_makeup)
    private val swipeRefresh: SwipeRefreshLayout
        get() = rootView!!.findViewById(R.id.swipe_refresh)

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val view = inflater.inflate(R.layout.fragment_makeup, container, false)
        rootView = view
        return view
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        adapter = MakeupTipAdapter()
        recyclerView.layoutManager = LinearLayoutManager(requireContext())
        recyclerView.adapter = adapter

        swipeRefresh.setOnRefreshListener { loadTips() }
        loadTips()
    }

    private fun loadTips() {
        swipeRefresh.isRefreshing = true
        PortalApp.instance.repository.getMakeupTips(selectedCategory)
            .observe(viewLifecycleOwner) { resource ->
                swipeRefresh.isRefreshing = false
                when (resource) {
                    is Resource.Success -> {
                        val response = resource.data as MakeupTipsResponse
                        allTips = response.tips
                        filterTips()
                        extractAndBuildCategoryChips()
                    }
                    is Resource.Error -> {
                        Snackbar.make(
                            rootView!!,
                            resource.message,
                            Snackbar.LENGTH_SHORT
                        ).show()
                    }
                    is Resource.Loading -> {
                        swipeRefresh.isRefreshing = true
                    }
                }
            }
    }

    private fun extractAndBuildCategoryChips() {
        val tipCategories = allTips.map { it.category }.distinct().sorted()
        val newCategories = listOf("All") + tipCategories

        if (newCategories == categories) return
        categories = newCategories

        chipGroupCategory.removeAllViews()
        categories.forEach { cat ->
            val chip = Chip(requireContext()).apply {
                text = cat
                isCheckable = true
                isChecked = cat == selectedCategory
                setOnClickListener {
                    selectedCategory = cat
                    filterTips()
                    // Rebuild chips to update checked state
                    chipGroupCategory.removeAllViews()
                    categories.forEach { c ->
                        val c2 = Chip(requireContext()).apply {
                            text = c
                            isCheckable = true
                            isChecked = c == selectedCategory
                            setOnClickListener {
                                selectedCategory = c
                                filterTips()
                            }
                        }
                        chipGroupCategory.addView(c2)
                    }
                }
            }
            chipGroupCategory.addView(chip)
        }
    }

    private fun filterTips() {
        val filtered = if (selectedCategory == "All") {
            allTips
        } else {
            allTips.filter {
                it.category.equals(selectedCategory, ignoreCase = true)
            }
        }
        adapter.submitList(filtered)
    }

    override fun onDestroyView() {
        super.onDestroyView()
        rootView = null
    }
}

class MakeupTipAdapter : RecyclerView.Adapter<MakeupTipAdapter.TipVH>() {

    private var items = listOf<MakeupTip>()
    private val expandedPositions = mutableSetOf<Int>()

    fun submitList(list: List<MakeupTip>) {
        items = list
        notifyDataSetChanged()
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): TipVH {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_makeup_tip, parent, false)
        return TipVH(view)
    }

    override fun onBindViewHolder(holder: TipVH, position: Int) {
        val item = items[position]
        val isExpanded = expandedPositions.contains(position)

        holder.tvTitle.text = item.title
        holder.chipCategory.text = item.category
        holder.chipDifficulty.text = item.difficulty
        holder.tvContent.text = item.content
        holder.tvContent.maxLines = if (isExpanded) Int.MAX_VALUE else 3

        holder.itemView.setOnClickListener {
            if (expandedPositions.contains(position)) {
                expandedPositions.remove(position)
            } else {
                expandedPositions.add(position)
            }
            notifyItemChanged(position)
        }
    }

    override fun getItemCount() = items.size

    class TipVH(view: View) : RecyclerView.ViewHolder(view) {
        val tvTitle: TextView = view.findViewById(R.id.tv_title)
        val chipCategory: Chip = view.findViewById(R.id.chip_category)
        val chipDifficulty: Chip = view.findViewById(R.id.chip_difficulty)
        val tvContent: TextView = view.findViewById(R.id.tv_content)
    }
}
