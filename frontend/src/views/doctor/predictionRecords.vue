<template>
    <div class="prediction-records">
        <el-card>
            <template #header>
                <div class="card-header">
                    <span>预测记录</span>
                </div>
            </template>

            <!-- 搜索和筛选 -->
            <div class="search-bar">
                <el-input
                    v-model="searchQuery"
                    placeholder="搜索患者姓名/ID"
                    style="width: 200px"
                    clearable
                    @clear="handleSearch"
                    @input="handleSearch"
                >
                    <template #prefix>
                        <el-icon><Search /></el-icon>
                    </template>
                </el-input>
                
                <el-date-picker
                    v-model="dateRange"
                    type="daterange"
                    range-separator="至"
                    start-placeholder="开始日期"
                    end-placeholder="结束日期"
                    @change="handleSearch"
                />
            </div>

            <!-- 记录列表 -->
            <el-table :data="recordsList" style="width: 100%" v-loading="loading">
                <el-table-column prop="id" label="记录ID" width="120" />
                <el-table-column prop="patientName" label="患者姓名" width="120" />
                <el-table-column prop="patientId" label="患者ID" width="120" />
                <el-table-column prop="predictionTime" label="预测时间" width="180" />
                <el-table-column prop="result" label="预测结果" width="120" />
                <el-table-column prop="accuracy" label="准确度" width="120">
                    <template #default="scope">
                        {{ scope.row.accuracy }}%
                    </template>
                </el-table-column>
                <el-table-column label="操作" fixed="right" width="150">
                    <template #default="scope">
                        <el-button type="primary" link @click="handleView(scope.row)">
                            查看详情
                        </el-button>
                        <el-button type="danger" link @click="handleDelete(scope.row)">
                            删除
                        </el-button>
                    </template>
                </el-table-column>
            </el-table>

            <!-- 分页 -->
            <div class="pagination">
                <el-pagination
                    v-model:current-page="currentPage"
                    v-model:page-size="pageSize"
                    :page-sizes="[10, 20, 30, 50]"
                    layout="total, sizes, prev, pager, next, jumper"
                    :total="total"
                    @size-change="handleSizeChange"
                    @current-change="handleCurrentChange"
                />
            </div>
        </el-card>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const searchQuery = ref('')
const dateRange = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const recordsList = ref([])

// 获取记录列表
const getRecordsList = async () => {
    loading.value = true
    try {
        // TODO: 调用后端API获取预测记录列表
        // const response = await axios.get('/api/prediction/records', {
        //     params: {
        //         page: currentPage.value,
        //         pageSize: pageSize.value,
        //         query: searchQuery.value,
        //         startDate: dateRange.value[0],
        //         endDate: dateRange.value[1]
        //     }
        // })
        // recordsList.value = response.data.list
        // total.value = response.data.total
    } catch (error) {
        ElMessage.error('获取预测记录失败')
    } finally {
        loading.value = false
    }
}

// 搜索处理
const handleSearch = () => {
    currentPage.value = 1
    getRecordsList()
}

// 分页处理
const handleSizeChange = (val) => {
    pageSize.value = val
    getRecordsList()
}

const handleCurrentChange = (val) => {
    currentPage.value = val
    getRecordsList()
}

// 查看详情
const handleView = (row) => {
    // TODO: 实现查看详情功能
}

// 删除记录
const handleDelete = (row) => {
    ElMessageBox.confirm(
        '确定要删除该预测记录吗？',
        '警告',
        {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning',
        }
    ).then(async () => {
        try {
            // TODO: 调用后端API删除记录
            // await axios.delete(`/api/prediction/records/${row.id}`)
            ElMessage.success('删除成功')
            getRecordsList()
        } catch (error) {
            ElMessage.error('删除失败')
        }
    }).catch(() => {})
}

onMounted(() => {
    getRecordsList()
})
</script>

<style scoped>
.prediction-records {
    padding: 20px;
}

.search-bar {
    margin-bottom: 20px;
    display: flex;
    gap: 20px;
}

.pagination {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
}
</style> 