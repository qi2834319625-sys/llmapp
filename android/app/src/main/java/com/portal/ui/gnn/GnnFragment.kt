package com.portal.ui.gnn

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
import com.portal.PortalApp
import com.portal.R
import com.portal.data.model.GnnEntity
import com.portal.data.model.GnnRelation
import com.portal.data.repository.Resource
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch

class GnnFragment : Fragment() {

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View? {
        return inflater.inflate(R.layout.fragment_gnn, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val rvEntities = view.findViewById<RecyclerView>(R.id.rv_entities)
        val rvRelations = view.findViewById<RecyclerView>(R.id.rv_relations)
        val btnAddEntity = view.findViewById<ImageButton>(R.id.btn_add_entity)
        val btnAddRelation = view.findViewById<ImageButton>(R.id.btn_add_relation)

        rvEntities?.layoutManager = LinearLayoutManager(requireContext())
        rvRelations?.layoutManager = LinearLayoutManager(requireContext())

        btnAddEntity?.setOnClickListener {
            val editText = EditText(requireContext()).apply { hint = "实体名称" }
            AlertDialog.Builder(requireContext())
                .setTitle("添加实体")
                .setView(editText)
                .setPositiveButton("添加") { _, _ ->
                    val name = editText.text.toString().trim()
                    if (name.isNotEmpty()) {
                        GlobalScope.launch {
                            PortalApp.instance.repository.addGnnEntity(name, "default")
                            loadEntities()
                        }
                    }
                }
                .setNegativeButton("取消", null)
                .show()
        }

        btnAddRelation?.setOnClickListener {
            val layout = LinearLayout(requireContext()).apply { orientation = LinearLayout.VERTICAL }
            val etSource = EditText(requireContext()).apply { hint = "源实体ID"; inputType = android.text.InputType.TYPE_CLASS_NUMBER }
            val etTarget = EditText(requireContext()).apply { hint = "目标实体ID"; inputType = android.text.InputType.TYPE_CLASS_NUMBER }
            val etType = EditText(requireContext()).apply { hint = "关系类型" }
            layout.addView(etSource)
            layout.addView(etTarget)
            layout.addView(etType)

            AlertDialog.Builder(requireContext())
                .setTitle("添加关系")
                .setView(layout)
                .setPositiveButton("添加") { _, _ ->
                    val sid = etSource.text.toString().toIntOrNull() ?: 0
                    val tid = etTarget.text.toString().toIntOrNull() ?: 0
                    val type = etType.text.toString().trim()
                    if (sid > 0 && tid > 0 && type.isNotEmpty()) {
                        GlobalScope.launch {
                            PortalApp.instance.repository.addGnnRelation(sid, tid, type)
                            loadRelations()
                        }
                    }
                }
                .setNegativeButton("取消", null)
                .show()
        }

        loadEntities()
        loadRelations()
    }

    private fun loadEntities() {
        GlobalScope.launch {
            PortalApp.instance.repository.getGnnEntities().observe(viewLifecycleOwner) { resource ->
                when (resource) {
                    is Resource.Success -> {
                        view?.findViewById<RecyclerView>(R.id.rv_entities)?.adapter =
                            EntityAdapter(resource.data)
                    }
                    is Resource.Error -> {}
                    is Resource.Loading -> {}
                }
            }
        }
    }

    private fun loadRelations() {
        GlobalScope.launch {
            PortalApp.instance.repository.getGnnRelations().observe(viewLifecycleOwner) { resource ->
                when (resource) {
                    is Resource.Success -> {
                        view?.findViewById<RecyclerView>(R.id.rv_relations)?.adapter =
                            RelationAdapter(resource.data)
                    }
                    is Resource.Error -> {}
                    is Resource.Loading -> {}
                }
            }
        }
    }

    class EntityAdapter(private val entities: List<GnnEntity>) : RecyclerView.Adapter<EntityAdapter.VH>() {
        class VH(view: View) : RecyclerView.ViewHolder(view) {
            val name: TextView = view.findViewById(R.id.tv_name)
            val type: Chip = view.findViewById(R.id.chip_type)
            val desc: TextView = view.findViewById(R.id.tv_description)
        }
        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
            val view = LayoutInflater.from(parent.context).inflate(R.layout.item_entity, parent, false)
            return VH(view)
        }
        override fun onBindViewHolder(holder: VH, position: Int) {
            val e = entities[position]
            holder.name.text = e.name
            holder.type.text = e.entityType
            holder.desc.text = e.description
        }
        override fun getItemCount() = entities.size
    }

    class RelationAdapter(private val relations: List<GnnRelation>) : RecyclerView.Adapter<RelationAdapter.VH>() {
        class VH(view: View) : RecyclerView.ViewHolder(view) {
            val relation: TextView = view.findViewById(R.id.tv_relation)
            val weight: TextView = view.findViewById(R.id.tv_weight)
        }
        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
            val view = LayoutInflater.from(parent.context).inflate(R.layout.item_relation, parent, false)
            return VH(view)
        }
        override fun onBindViewHolder(holder: VH, position: Int) {
            val r = relations[position]
            holder.relation.text = "${r.sourceName} → [${r.relationType}] → ${r.targetName}"
            holder.weight.text = "权重: ${r.weight}"
        }
        override fun getItemCount() = relations.size
    }
}
