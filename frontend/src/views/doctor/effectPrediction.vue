<template>
    <div class="effect-prediction">
        <el-card class="prediction-form">
            <template #header>
                <div class="card-header">
                    <span>手术效果预测</span>
                </div>
            </template>
            
            <el-form
                ref="predictionFormRef"
                :model="predictionForm"
                :rules="rules"
                label-width="120px"
            >
                <!-- 基本信息 -->
                <el-divider>基本信息</el-divider>
                <el-form-item label="患者" prop="patientId">
                    <el-select
                        v-model="predictionForm.patientId"
                        placeholder="请选择患者"
                        filterable
                    >
                        <el-option
                            v-for="patient in patientList"
                            :key="patient.id"
                            :label="patient.name"
                            :value="patient.id"
                        />
                    </el-select>
                </el-form-item>

                <!-- 临床指标 -->
                <el-divider>临床指标</el-divider>
                <el-form-item label="PSA" prop="psa">
                    <el-input-number
                        v-model="predictionForm.psa"
                        :precision="2"
                        :step="0.1"
                        :min="0"
                    />
                </el-form-item>

                <!-- 更多临床指标... -->

                <el-form-item>
                    <el-button type="primary" @click="submitForm">
                        开始预测
                    </el-button>
                    <el-button @click="resetForm">重置</el-button>
                </el-form-item>
            </el-form>
        </el-card>

        <!-- 预测结果 -->
        <el-card v-if="showResult" class="prediction-result">
            <template #header>
                <div class="card-header">
                    <span>预测结果</span>
                </div>
            </template>
            <!-- 预测结果内容 -->
        </el-card>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const predictionFormRef = ref(null)
const showResult = ref(false)
const patientList = ref([])

const predictionForm = ref({
    patientId: '',
    psa: null,
    // 更多字段...
})

const rules = {
    patientId: [
        { required: true, message: '请选择患者', trigger: 'change' }
    ],
    psa: [
        { required: true, message: '请输入PSA值', trigger: 'blur' }
    ],
}

// 获取患者列表
const getPatientList = async () => {
    try {
        // TODO: 调用后端API获取患者列表
        // const response = await axios.get('/api/patients/list')
        // patientList.value = response.data
    } catch (error) {
        ElMessage.error('获取患者列表失败')
    }
}

// 提交预测
const submitForm = async () => {
    if (!predictionFormRef.value) return
    
    await predictionFormRef.value.validate(async (valid) => {
        if (valid) {
            try {
                // TODO: 调用后端预测API
                // const response = await axios.post('/api/prediction', predictionForm.value)
                showResult.value = true
                ElMessage.success('预测完成')
            } catch (error) {
                ElMessage.error('预测失败')
            }
        }
    })
}

// 重置表单
const resetForm = () => {
    if (predictionFormRef.value) {
        predictionFormRef.value.resetFields()
    }
    showResult.value = false
}

onMounted(() => {
    getPatientList()
})
</script>

<style scoped>
.effect-prediction {
    padding: 20px;
    display: flex;
    gap: 20px;
}

.prediction-form {
    flex: 1;
}

.prediction-result {
    flex: 1;
}

.el-divider {
    margin: 20px 0;
}
</style> 