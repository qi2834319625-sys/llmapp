package com.portal.ui.investment

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
import com.google.android.material.floatingactionbutton.FloatingActionButton
import com.google.android.material.snackbar.Snackbar
import com.portal.PortalApp
import com.portal.R
import com.portal.data.model.InvestmentRecord
import com.portal.data.repository.Resource
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch
import java.text.NumberFormat
import java.util.Locale

class InvestmentFragment : Fragment() {

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View? {
        return inflater.inflate(R.layout.fragment_investment, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val swipeRefresh = view.findViewById<androidx.swiperefreshlayout.widget.SwipeRefreshLayout>(R.id.swipe_refresh)
        val recyclerView = view.findViewById<RecyclerView>(R.id.rv_investment)
        recyclerView?.layoutManager = LinearLayoutManager(requireContext())

        view.findViewById<FloatingActionButton>(R.id.fab_add_investment)?.setOnClickListener {
            showAddDialog()
        }

        swipeRefresh?.setOnRefreshListener { loadRecords() }
        loadRecords()
    }

    private fun loadRecords() {
        view?.findViewById<androidx.swiperefreshlayout.widget.SwipeRefreshLayout>(R.id.swipe_refresh)?.isRefreshing = true
        GlobalScope.launch {
            PortalApp.instance.repository.getInvestmentRecords().observe(viewLifecycleOwner) { resource ->
                view?.findViewById<androidx.swiperefreshlayout.widget.SwipeRefreshLayout>(R.id.swipe_refresh)?.isRefreshing = false
                when (resource) {
                    is Resource.Success -> {
                        val records = resource.data
                        updateSummary(records)
                        view?.findViewById<RecyclerView>(R.id.rv_investment)?.adapter = InvestmentAdapter(records)
                    }
                    is Resource.Error -> {
                        view?.post { Snackbar.make(requireView(), "加载失败: ${resource.message}", Snackbar.LENGTH_SHORT).show() }
                    }
                    is Resource.Loading -> {}
                }
            }
        }
    }

    private fun updateSummary(records: List<InvestmentRecord>) {
        val total = records.sumOf { it.amount }
        val avgReturn = if (records.isNotEmpty()) records.map { it.returnRate }.average() else 0.0
        val fmt = NumberFormat.getCurrencyInstance(Locale.CHINA)

        view?.findViewById<TextView>(R.id.tv_record_count)?.text = "共 ${records.size} 条记录"
        view?.findViewById<TextView>(R.id.tv_portfolio_total)?.text = "总资产: ${fmt.format(total)}"
        view?.findViewById<TextView>(R.id.tv_avg_return)?.text = "平均收益率: ${String.format("%.2f", avgReturn)}%"
    }

    private fun showAddDialog() {
        val layout = LinearLayout(requireContext()).apply { orientation = LinearLayout.VERTICAL; setPadding(48, 32, 48, 0) }
        val etName = EditText(requireContext()).apply { hint = "名称" }
        val etAmount = EditText(requireContext()).apply { hint = "金额"; inputType = android.text.InputType.TYPE_CLASS_NUMBER or android.text.InputType.TYPE_NUMBER_FLAG_DECIMAL }
        val etReturn = EditText(requireContext()).apply { hint = "收益率 (%)"; inputType = android.text.InputType.TYPE_CLASS_NUMBER or android.text.InputType.TYPE_NUMBER_FLAG_DECIMAL or android.text.InputType.TYPE_NUMBER_FLAG_SIGNED }
        layout.addView(etName)
        layout.addView(etAmount)
        layout.addView(etReturn)

        AlertDialog.Builder(requireContext())
            .setTitle("添加投资记录")
            .setView(layout)
            .setPositiveButton("添加") { _, _ ->
                val name = etName.text.toString().trim()
                val amount = etAmount.text.toString().toDoubleOrNull() ?: 0.0
                val ret = etReturn.text.toString().toDoubleOrNull() ?: 0.0
                if (name.isNotEmpty() && amount > 0) {
                    GlobalScope.launch {
                        PortalApp.instance.repository.addInvestment(name, "Stock", amount, ret, "Medium", "")
                        loadRecords()
                    }
                }
            }
            .setNegativeButton("取消", null)
            .show()
    }

    class InvestmentAdapter(private val records: List<InvestmentRecord>) : RecyclerView.Adapter<InvestmentAdapter.VH>() {
        class VH(view: View) : RecyclerView.ViewHolder(view) {
            val name: TextView = view.findViewById(R.id.tv_name)
            val assetType: Chip = view.findViewById(R.id.chip_asset_type)
            val amount: TextView = view.findViewById(R.id.tv_amount)
            val returnRate: TextView = view.findViewById(R.id.tv_return_rate)
            val risk: TextView = view.findViewById(R.id.tv_risk)
        }
        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
            val view = LayoutInflater.from(parent.context).inflate(R.layout.item_investment, parent, false)
            return VH(view)
        }
        override fun onBindViewHolder(holder: VH, position: Int) {
            val r = records[position]
            holder.name.text = r.name
            holder.assetType.text = r.assetType
            holder.amount.text = NumberFormat.getCurrencyInstance(Locale.CHINA).format(r.amount)
            holder.returnRate.text = "${if (r.returnRate > 0) "+" else ""}${String.format("%.2f", r.returnRate)}%"
            holder.returnRate.setTextColor(if (r.returnRate > 0) 0xFF4CAF50.toInt() else 0xFFF44336.toInt())
            holder.risk.text = r.riskLevel
        }
        override fun getItemCount() = records.size
    }
}
