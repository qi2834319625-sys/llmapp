package com.portal.ui.studyabroad

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
import com.portal.data.model.StudyAbroadProgram
import com.portal.data.repository.Resource
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch

class StudyAbroadFragment : Fragment() {

    private var allPrograms: List<StudyAbroadProgram> = emptyList()
    private var currentCountry = ""

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View? {
        return inflater.inflate(R.layout.fragment_study_abroad, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val swipeRefresh = view.findViewById<androidx.swiperefreshlayout.widget.SwipeRefreshLayout>(R.id.swipe_refresh)
        val recyclerView = view.findViewById<RecyclerView>(R.id.rv_study_abroad)
        recyclerView?.layoutManager = LinearLayoutManager(requireContext())

        // Country filter chips
        val chipGroup = com.google.android.material.chip.ChipGroup(requireContext()).apply {
            setPadding(16, 16, 16, 16)
        }
        val countries = listOf("All", "USA", "UK", "Canada", "Australia", "Germany", "Japan", "Singapore")
        countries.forEach { country ->
            val chip = com.google.android.material.chip.Chip(requireContext()).apply {
                text = country
                isCheckable = true
                isChecked = country == "All"
                setOnClickListener {
                    currentCountry = if (country == "All") "" else country
                    loadPrograms()
                }
            }
            chipGroup.addView(chip)
        }

        val rootLayout = view as? ViewGroup
        rootLayout?.addView(chipGroup, 0)

        swipeRefresh?.setOnRefreshListener { loadPrograms() }
        loadPrograms()
    }

    private fun loadPrograms() {
        view?.findViewById<androidx.swiperefreshlayout.widget.SwipeRefreshLayout>(R.id.swipe_refresh)?.isRefreshing = true
        GlobalScope.launch {
            PortalApp.instance.repository.getStudyAbroad(currentCountry).observe(viewLifecycleOwner) { resource ->
                view?.findViewById<androidx.swiperefreshlayout.widget.SwipeRefreshLayout>(R.id.swipe_refresh)?.isRefreshing = false
                when (resource) {
                    is Resource.Success -> {
                        allPrograms = resource.data.programs
                        view?.findViewById<RecyclerView>(R.id.rv_study_abroad)?.adapter = ProgramAdapter(allPrograms)
                    }
                    is Resource.Error -> {
                        view?.post { Snackbar.make(requireView(), "加载失败: ${resource.message}", Snackbar.LENGTH_SHORT).show() }
                    }
                    is Resource.Loading -> {}
                }
            }
        }
    }

    class ProgramAdapter(private val programs: List<StudyAbroadProgram>) : RecyclerView.Adapter<ProgramAdapter.VH>() {
        class VH(view: View) : RecyclerView.ViewHolder(view) {
            val flag: TextView = view.findViewById(R.id.tv_flag)
            val university: TextView = view.findViewById(R.id.tv_university)
            val program: TextView = view.findViewById(R.id.tv_program)
            val requirements: TextView = view.findViewById(R.id.tv_requirements)
            val deadline: TextView = view.findViewById(R.id.tv_deadline)
        }
        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
            val view = LayoutInflater.from(parent.context).inflate(R.layout.item_program, parent, false)
            return VH(view)
        }
        override fun onBindViewHolder(holder: VH, position: Int) {
            val p = programs[position]
            holder.flag.text = getFlagEmoji(p.country)
            holder.university.text = p.university
            holder.program.text = p.program
            holder.requirements.text = p.requirements.take(100)
            holder.deadline.text = "截止: ${p.deadline}"
        }
        override fun getItemCount() = programs.size

        private fun getFlagEmoji(country: String): String {
            return when (country.lowercase()) {
                "usa", "us" -> "🇺🇸"
                "uk", "gb" -> "🇬🇧"
                "canada", "ca" -> "🇨🇦"
                "australia", "au" -> "🇦🇺"
                "germany", "de" -> "🇩🇪"
                "japan", "jp" -> "🇯🇵"
                "singapore", "sg" -> "🇸🇬"
                else -> "🌍"
            }
        }
    }
}
