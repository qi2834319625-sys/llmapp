package com.portal.ui.fashion

import android.graphics.Color
import android.graphics.drawable.GradientDrawable
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
import com.portal.data.model.FashionItem
import com.portal.data.model.FashionItemsResponse
import com.portal.data.repository.Resource

class FashionFragment : Fragment() {

    private var rootView: View? = null
    private lateinit var adapter: FashionAdapter
    private var allItems = listOf<FashionItem>()
    private var selectedSeason = "All"
    private var selectedStyle = "All"

    private val chipGroupSeason: ChipGroup
        get() = rootView!!.findViewById(R.id.chip_group_season)
    private val chipGroupStyle: ChipGroup
        get() = rootView!!.findViewById(R.id.chip_group_style)
    private val recyclerView: RecyclerView
        get() = rootView!!.findViewById(R.id.rv_fashion)
    private val swipeRefresh: androidx.swiperefreshlayout.widget.SwipeRefreshLayout
        get() = rootView!!.findViewById(R.id.swipe_refresh)

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val view = inflater.inflate(R.layout.fragment_fashion, container, false)
        rootView = view
        return view
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        adapter = FashionAdapter()
        recyclerView.layoutManager = LinearLayoutManager(requireContext())
        recyclerView.adapter = adapter

        setupSeasonChips()
        setupStyleChips()

        swipeRefresh.setOnRefreshListener { loadItems() }
        loadItems()
    }

    private fun setupSeasonChips() {
        chipGroupSeason.removeAllViews()
        val seasons = listOf("All", "Spring", "Summer", "Autumn", "Winter")
        seasons.forEach { s ->
            val chip = Chip(requireContext()).apply {
                text = s
                isCheckable = true
                isChecked = s == selectedSeason
                setOnClickListener {
                    selectedSeason = s
                    rebuildSeasonChips()
                    filterItems()
                }
            }
            chipGroupSeason.addView(chip)
        }
    }

    private fun rebuildSeasonChips() {
        chipGroupSeason.removeAllViews()
        val seasons = listOf("All", "Spring", "Summer", "Autumn", "Winter")
        seasons.forEach { s ->
            val chip = Chip(requireContext()).apply {
                text = s
                isCheckable = true
                isChecked = s == selectedSeason
                setOnClickListener {
                    selectedSeason = s
                    rebuildSeasonChips()
                    filterItems()
                }
            }
            chipGroupSeason.addView(chip)
        }
    }

    private fun setupStyleChips() {
        chipGroupStyle.removeAllViews()
        val styles = listOf("All", "Casual", "Formal", "Sporty", "Vintage")
        styles.forEach { s ->
            val chip = Chip(requireContext()).apply {
                text = s
                isCheckable = true
                isChecked = s == selectedStyle
                setOnClickListener {
                    selectedStyle = s
                    rebuildStyleChips()
                    filterItems()
                }
            }
            chipGroupStyle.addView(chip)
        }
    }

    private fun rebuildStyleChips() {
        chipGroupStyle.removeAllViews()
        val styles = listOf("All", "Casual", "Formal", "Sporty", "Vintage")
        styles.forEach { s ->
            val chip = Chip(requireContext()).apply {
                text = s
                isCheckable = true
                isChecked = s == selectedStyle
                setOnClickListener {
                    selectedStyle = s
                    rebuildStyleChips()
                    filterItems()
                }
            }
            chipGroupStyle.addView(chip)
        }
    }

    private fun loadItems() {
        swipeRefresh.isRefreshing = true
        PortalApp.instance.repository.getFashionItems(selectedSeason, selectedStyle)
            .observe(viewLifecycleOwner) { resource ->
                when (resource) {
                    is Resource.Success -> {
                        swipeRefresh.isRefreshing = false
                        val response = resource.data as FashionItemsResponse
                        allItems = response.items
                        filterItems()
                    }
                    is Resource.Error -> {
                        swipeRefresh.isRefreshing = false
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

    private fun filterItems() {
        val filtered = allItems.filter { item ->
            val matchesSeason = selectedSeason == "All" ||
                item.season.equals(selectedSeason, ignoreCase = true)
            val matchesStyle = selectedStyle == "All" ||
                item.style.equals(selectedStyle, ignoreCase = true)
            matchesSeason && matchesStyle
        }
        adapter.submitList(filtered)
    }

    override fun onDestroyView() {
        super.onDestroyView()
        rootView = null
    }
}

class FashionAdapter : RecyclerView.Adapter<FashionAdapter.FVH>() {

    private var items = listOf<FashionItem>()

    fun submitList(list: List<FashionItem>) {
        items = list
        notifyDataSetChanged()
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): FVH {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_fashion, parent, false)
        return FVH(view)
    }

    override fun onBindViewHolder(holder: FVH, position: Int) {
        val item = items[position]

        holder.tvName.text = buildString {
            append(item.name)
            if (item.category.isNotEmpty()) {
                append("  (")
                append(item.category)
                append(")")
            }
        }
        holder.chipSeason.text = item.season
        holder.tvStyle.text = item.style
        holder.tvDescription.text = item.description

        // Color dot
        try {
            val color = if (!item.color.isNullOrEmpty()) {
                Color.parseColor(item.color)
            } else {
                Color.LTGRAY
            }
            val bg = GradientDrawable().apply {
                setColor(color)
                setStroke(2, Color.DKGRAY)
                cornerRadius = 50f
            }
            holder.viewColor.background = bg
        } catch (e: Exception) {
            holder.viewColor.setBackgroundColor(Color.LTGRAY)
        }
    }

    override fun getItemCount() = items.size

    class FVH(view: View) : RecyclerView.ViewHolder(view) {
        val tvName: TextView = view.findViewById(R.id.tv_name)
        val chipSeason: Chip = view.findViewById(R.id.chip_season)
        val viewColor: View = view.findViewById(R.id.view_color)
        val tvStyle: TextView = view.findViewById(R.id.tv_style)
        val tvDescription: TextView = view.findViewById(R.id.tv_description)
    }
}
