package com.portal.ui.cooking

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.LinearLayout
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.card.MaterialCardView
import com.google.android.material.chip.Chip
import com.google.android.material.chip.ChipGroup
import com.google.android.material.snackbar.Snackbar
import com.portal.PortalApp
import com.portal.R
import com.portal.data.model.Recipe
import com.portal.data.repository.Resource

class CookingFragment : Fragment() {

    private lateinit var chipGroupCuisine: ChipGroup
    private lateinit var chipGroupDifficulty: ChipGroup
    private lateinit var rvCooking: RecyclerView
    private lateinit var adapter: RecipeAdapter
    private var allRecipes = listOf<Recipe>()
    private var selectedCuisine = "All"
    private var selectedDifficulty = "All"

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.fragment_cooking, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        chipGroupCuisine = view.findViewById(R.id.chip_group_cuisine)
        chipGroupDifficulty = view.findViewById(R.id.chip_group_difficulty)
        rvCooking = view.findViewById(R.id.rv_cooking)

        adapter = RecipeAdapter()
        rvCooking.layoutManager = LinearLayoutManager(requireContext())
        rvCooking.adapter = adapter

        // Cuisine filter chips
        setupCuisineChips()

        // Difficulty filter chips
        setupDifficultyChips()

        loadRecipes()
    }

    private fun setupCuisineChips() {
        chipGroupCuisine.removeAllViews()
        val cuisines = listOf("All", "Chinese", "Japanese", "Korean", "Western", "Thai", "Italian")
        cuisines.forEach { c ->
            val chip = Chip(requireContext()).apply {
                text = c
                isCheckable = true
                isChecked = c == selectedCuisine
                setOnClickListener {
                    selectedCuisine = c
                    rebuildCuisineChips()
                    filterRecipes()
                }
            }
            chipGroupCuisine.addView(chip)
        }
    }

    private fun rebuildCuisineChips() {
        chipGroupCuisine.removeAllViews()
        val cuisines = listOf("All", "Chinese", "Japanese", "Korean", "Western", "Thai", "Italian")
        cuisines.forEach { c ->
            val chip = Chip(requireContext()).apply {
                text = c
                isCheckable = true
                isChecked = c == selectedCuisine
                setOnClickListener {
                    selectedCuisine = c
                    rebuildCuisineChips()
                    filterRecipes()
                }
            }
            chipGroupCuisine.addView(chip)
        }
    }

    private fun setupDifficultyChips() {
        chipGroupDifficulty.removeAllViews()
        val difficulties = listOf("All", "Easy", "Medium", "Hard")
        difficulties.forEach { d ->
            val chip = Chip(requireContext()).apply {
                text = d
                isCheckable = true
                isChecked = d == selectedDifficulty
                setOnClickListener {
                    selectedDifficulty = d
                    rebuildDifficultyChips()
                    filterRecipes()
                }
            }
            chipGroupDifficulty.addView(chip)
        }
    }

    private fun rebuildDifficultyChips() {
        chipGroupDifficulty.removeAllViews()
        val difficulties = listOf("All", "Easy", "Medium", "Hard")
        difficulties.forEach { d ->
            val chip = Chip(requireContext()).apply {
                text = d
                isCheckable = true
                isChecked = d == selectedDifficulty
                setOnClickListener {
                    selectedDifficulty = d
                    rebuildDifficultyChips()
                    filterRecipes()
                }
            }
            chipGroupDifficulty.addView(chip)
        }
    }

    private fun loadRecipes() {
        PortalApp.instance.repository.getRecipes(
            cuisine = if (selectedCuisine == "All") "" else selectedCuisine,
            difficulty = if (selectedDifficulty == "All") "" else selectedDifficulty
        ).observe(viewLifecycleOwner) { resource ->
            when (resource) {
                is Resource.Success -> {
                    allRecipes = resource.data.recipes
                    filterRecipes()
                }
                is Resource.Error -> {
                    val rootView = view
                    if (rootView != null) {
                        Snackbar.make(rootView, resource.message, Snackbar.LENGTH_SHORT).show()
                    }
                }
                is Resource.Loading -> {
                    // Show loading state
                }
            }
        }
    }

    private fun filterRecipes() {
        val filtered = allRecipes.filter { recipe ->
            val matchesCuisine = selectedCuisine == "All" ||
                recipe.cuisine.equals(selectedCuisine, ignoreCase = true)
            val matchesDifficulty = selectedDifficulty == "All" ||
                recipe.difficulty.equals(selectedDifficulty, ignoreCase = true)
            matchesCuisine && matchesDifficulty
        }
        adapter.submitList(filtered)
    }
}

class RecipeAdapter : RecyclerView.Adapter<RecipeAdapter.RecipeVH>() {

    private var items = listOf<Recipe>()
    private val expandedPositions = mutableSetOf<Int>()

    fun submitList(list: List<Recipe>) {
        items = list
        notifyDataSetChanged()
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RecipeVH {
        val density = parent.context.resources.displayMetrics.density

        val card = MaterialCardView(parent.context).apply {
            layoutParams = ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT
            )
            val margin = (8 * density).toInt()
            (layoutParams as ViewGroup.MarginLayoutParams).setMargins(margin, margin, margin, margin)
            cardElevation = (2 * density)
            radius = (12 * density)
        }

        val container = LinearLayout(parent.context).apply {
            orientation = LinearLayout.VERTICAL
            val padding = (16 * density).toInt()
            setPadding(padding, padding, padding, padding)
        }

        // Recipe name
        val tvName = TextView(parent.context).apply {
            id = View.generateViewId()
            textSize = 16f
            setTypeface(null, android.graphics.Typeface.BOLD)
        }
        container.addView(tvName)

        // Info row: cuisine chip, difficulty, cook time
        val infoRow = LinearLayout(parent.context).apply {
            orientation = LinearLayout.HORIZONTAL
        }
        val infoRowParams = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply { topMargin = (8 * density).toInt() }
        container.addView(infoRow, infoRowParams)

        val chipCuisine = Chip(parent.context).apply {
            id = View.generateViewId()
            textSize = 12f
            isClickable = false
            isCheckable = false
        }
        infoRow.addView(chipCuisine)

        val tvDifficulty = TextView(parent.context).apply {
            id = View.generateViewId()
            textSize = 12f
            setTextColor(android.graphics.Color.parseColor("#757575"))
        }
        val diffParams = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.WRAP_CONTENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply {
            marginStart = (8 * density).toInt()
            gravity = android.view.Gravity.CENTER_VERTICAL
        }
        infoRow.addView(tvDifficulty, diffParams)

        val tvCookTime = TextView(parent.context).apply {
            id = View.generateViewId()
            textSize = 12f
            setTextColor(android.graphics.Color.parseColor("#9E9E9E"))
        }
        val timeParams = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.WRAP_CONTENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply {
            marginStart = (8 * density).toInt()
            gravity = android.view.Gravity.CENTER_VERTICAL
        }
        infoRow.addView(tvCookTime, timeParams)

        // Ingredients preview
        val tvIngredientsPreview = TextView(parent.context).apply {
            id = View.generateViewId()
            textSize = 14f
            maxLines = 3
            setTextColor(android.graphics.Color.parseColor("#424242"))
        }
        val previewParams = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply { topMargin = (8 * density).toInt() }
        container.addView(tvIngredientsPreview, previewParams)

        // Full ingredients (expandable)
        val tvIngredients = TextView(parent.context).apply {
            id = View.generateViewId()
            textSize = 14f
            visibility = View.GONE
            setTextColor(android.graphics.Color.parseColor("#424242"))
        }
        val ingParams = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply { topMargin = (8 * density).toInt() }
        container.addView(tvIngredients, ingParams)

        // Steps (expandable)
        val tvSteps = TextView(parent.context).apply {
            id = View.generateViewId()
            textSize = 14f
            visibility = View.GONE
            setTextColor(android.graphics.Color.parseColor("#424242"))
        }
        val stepsParams = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply { topMargin = (8 * density).toInt() }
        container.addView(tvSteps, stepsParams)

        // Tips (expandable)
        val tvTips = TextView(parent.context).apply {
            id = View.generateViewId()
            textSize = 13f
            visibility = View.GONE
            setTextColor(android.graphics.Color.parseColor("#795548"))
        }
        val tipsParams = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply { topMargin = (8 * density).toInt() }
        container.addView(tvTips, tipsParams)

        card.addView(container)

        return RecipeVH(
            card, tvName, chipCuisine, tvDifficulty, tvCookTime,
            tvIngredientsPreview, tvIngredients, tvSteps, tvTips
        )
    }

    override fun onBindViewHolder(holder: RecipeVH, position: Int) {
        val item = items[position]
        val isExpanded = expandedPositions.contains(position)

        holder.tvName.text = item.name
        holder.chipCuisine.text = item.cuisine
        holder.tvDifficulty.text = item.difficulty
        holder.tvCookTime.text = if (item.cookTime > 0) "${item.cookTime} min" else ""

        // Ingredients preview (first 3 lines)
        val ingredientsLines = item.ingredients.split("\n").filter { it.isNotBlank() }
        val preview = ingredientsLines.take(3).joinToString("\n")
        val hasMore = ingredientsLines.size > 3
        holder.tvIngredientsPreview.text = if (hasMore) {
            "$preview\n..."
        } else {
            preview
        }

        // Expanded content
        if (isExpanded) {
            holder.tvIngredients.text = item.ingredients
            holder.tvSteps.text = item.steps
            holder.tvTips.text = item.tips
            holder.tvIngredients.visibility = View.VISIBLE
            holder.tvSteps.visibility = View.VISIBLE
            holder.tvTips.visibility = View.VISIBLE
            holder.tvIngredientsPreview.visibility = View.GONE
        } else {
            holder.tvIngredients.visibility = View.GONE
            holder.tvSteps.visibility = View.GONE
            holder.tvTips.visibility = View.GONE
            holder.tvIngredientsPreview.visibility = View.VISIBLE
        }

        holder.root.setOnClickListener {
            if (expandedPositions.contains(position)) {
                expandedPositions.remove(position)
            } else {
                expandedPositions.add(position)
            }
            notifyItemChanged(position)
        }
    }

    override fun getItemCount() = items.size

    class RecipeVH(
        val root: View,
        val tvName: TextView,
        val chipCuisine: Chip,
        val tvDifficulty: TextView,
        val tvCookTime: TextView,
        val tvIngredientsPreview: TextView,
        val tvIngredients: TextView,
        val tvSteps: TextView,
        val tvTips: TextView
    ) : RecyclerView.ViewHolder(root)
}
