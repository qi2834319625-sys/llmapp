package com.portal.ui.civilexam

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
import com.portal.PortalApp
import com.portal.R
import com.portal.data.model.CivilExamTopic
import com.portal.data.repository.Resource
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch

class CivilExamFragment : Fragment() {

    private var allTopics: List<CivilExamTopic> = emptyList()
    private var currentSubject = ""

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View? {
        return inflater.inflate(R.layout.fragment_civil_exam, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val swipeRefresh = view.findViewById<androidx.swiperefreshlayout.widget.SwipeRefreshLayout>(R.id.swipe_refresh)
        val recyclerView = view.findViewById<RecyclerView>(R.id.rv_civil_exam)
        recyclerView?.layoutManager = LinearLayoutManager(requireContext())

        // Create filter chips programmatically
        val chipGroup = ChipGroup(requireContext()).apply {
            id = View.generateViewId()
            setPadding(16, 16, 16, 16)
        }
        val subjects = listOf("All", "行测", "申论", "面试", "公基", "时政")
        subjects.forEach { subject ->
            val chip = Chip(requireContext()).apply {
                text = subject
                isCheckable = true
                isChecked = subject == "All"
                setOnClickListener {
                    currentSubject = if (subject == "All") "" else subject
                    filterTopics()
                }
            }
            chipGroup.addView(chip)
        }

        // Add chipgroup to layout
        val rootLayout = view as? ViewGroup
        rootLayout?.addView(chipGroup, 0)

        swipeRefresh?.setOnRefreshListener { loadTopics() }
        loadTopics()
    }

    private fun loadTopics() {
        view?.findViewById<androidx.swiperefreshlayout.widget.SwipeRefreshLayout>(R.id.swipe_refresh)?.isRefreshing = true
        GlobalScope.launch {
            PortalApp.instance.repository.getCivilExam("").observe(viewLifecycleOwner) { resource ->
                view?.findViewById<androidx.swiperefreshlayout.widget.SwipeRefreshLayout>(R.id.swipe_refresh)?.isRefreshing = false
                when (resource) {
                    is Resource.Success -> {
                        allTopics = resource.data.topics
                        filterTopics()
                    }
                    is Resource.Error -> {
                        view?.post { Snackbar.make(requireView(), "加载失败: ${resource.message}", Snackbar.LENGTH_SHORT).show() }
                    }
                    is Resource.Loading -> {}
                }
            }
        }
    }

    private fun filterTopics() {
        val filtered = if (currentSubject.isEmpty()) allTopics else allTopics.filter { it.subject == currentSubject }
        view?.findViewById<RecyclerView>(R.id.rv_civil_exam)?.adapter = TopicAdapter(filtered)
    }

    class TopicAdapter(private val topics: List<CivilExamTopic>) : RecyclerView.Adapter<TopicAdapter.VH>() {
        class VH(view: View) : RecyclerView.ViewHolder(view) {
            val subject: Chip = view.findViewById(R.id.chip_subject)
            val topic: TextView = view.findViewById(R.id.tv_topic)
            val content: TextView = view.findViewById(R.id.tv_content)
            val type: Chip = view.findViewById(R.id.chip_question_type)
        }
        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
            val view = LayoutInflater.from(parent.context).inflate(R.layout.item_topic, parent, false)
            return VH(view)
        }
        override fun onBindViewHolder(holder: VH, position: Int) {
            val t = topics[position]
            holder.subject.text = t.subject
            holder.topic.text = t.topic
            holder.content.text = t.content.take(100)
            holder.type.text = t.questionType
        }
        override fun getItemCount() = topics.size
    }
}
