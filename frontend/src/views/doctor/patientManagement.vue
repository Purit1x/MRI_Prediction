<template>
    <div class="patient-management">
        <el-card class="patient-list">
            <template #header>
                <div class="card-header">
                    <span>患者列表</span>
                    <el-button type="primary" @click="handleAddPatient">
                        添加患者
                    </el-button>
                </div>
            </template>
            
            <!-- 搜索栏 -->
            <div class="search-bar">
                <el-input
                    v-model="searchQuery"
                    placeholder="搜索患者姓名/ID"
                    clearable
                    @clear="handleSearch"
                    @input="handleSearch"
                >
                    <template #prefix>
                        <el-icon><Search /></el-icon>
                    </template>
                </el-input>
            </div>

            <!-- 患者列表表格 -->
            <el-table :data="patientList" style="width: 100%" v-loading="loading">
                <el-table-column prop="id" label="患者ID" width="120" />
                <el-table-column prop="name" label="姓名" width="120" />
                <el-table-column prop="age" label="年龄" width="80" />
                <el-table-column prop="gender" label="性别" width="80" />
                <el-table-column prop="phone" label="联系电话" width="150" />
                <el-table-column prop="createTime" label="创建时间" width="180" />
                <el-table-column label="操作" fixed="right" width="200">
                    <template #default="scope">
                        <el-button type="primary" link @click="handleView(scope.row)">
                            查看
                        </el-button>
                        <el-button type="primary" link @click="handleEdit(scope.row)">
                            编辑
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

// 数据
const loading = ref(false)
const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const patientList = ref([])

// 获取患者列表
const getPatientList = async () => {
    loading.value = true
    try {
        // TODO: 调用后端API获取患者列表
        // const response = await axios.get('/api/patients', {
        //     params: {
        //         page: currentPage.value,
        //         pageSize: pageSize.value,
        //         query: searchQuery.value
        //     }
        // })
        // patientList.value = response.data.list
        // total.value = response.data.total
    } catch (error) {
        ElMessage.error('获取患者列表失败')
    } finally {
        loading.value = false
    }
}

// 搜索处理
const handleSearch = () => {
    currentPage.value = 1
    getPatientList()
}

// 分页处理
const handleSizeChange = (val) => {
    pageSize.value = val
    getPatientList()
}

const handleCurrentChange = (val) => {
    currentPage.value = val
    getPatientList()
}

// 添加患者
const handleAddPatient = () => {
    // TODO: 实现添加患者功能
}

// 查看患者
const handleView = (row) => {
    // TODO: 实现查看患者详情功能
}

// 编辑患者
const handleEdit = (row) => {
    // TODO: 实现编辑患者功能
}

// 删除患者
const handleDelete = (row) => {
    ElMessageBox.confirm(
        '确定要删除该患者吗？',
        '警告',
        {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning',
        }
    ).then(async () => {
        try {
            // TODO: 调用后端API删除患者
            // await axios.delete(`/api/patients/${row.id}`)
            ElMessage.success('删除成功')
            getPatientList()
        } catch (error) {
            ElMessage.error('删除失败')
        }
    }).catch(() => {})
}

onMounted(() => {
    getPatientList()
})
</script>

<style scoped>
.patient-management {
    padding: 20px;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.search-bar {
    margin-bottom: 20px;
}

.pagination {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
}
</style> 