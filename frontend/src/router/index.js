import {
    createRouter,
    createWebHistory
} from 'vue-router'
import store from '@/stores/index.js'

// 使用动态导入
const login = () => import('@/views/doctor/login.vue')
const doctorHome = () => import('@/views/doctor/doctorHome.vue')
const patientManagement = () => import('@/views/doctor/patientManagement.vue')
const effectPrediction = () => import('@/views/doctor/effectPrediction.vue')
const predictionRecords = () => import('@/views/doctor/predictionRecords.vue')
const doctorProfile = () => import('@/views/doctor/doctorProfile.vue')

const routers = [
    {
        path: '/',
        redirect: '/patient-management'
    },
    {
        path: '/login',
        name: 'login',
        component: login,
        meta: {
            title: '登录页面',
            requiresAuth: false
        }
    },
    {
        path: '/doctorHome',
        name: 'doctorHome',
        component: doctorHome,
        redirect: '/patient-management',
        children: [
            {
                path: '/patient-management',
                name: 'patientManagement',
                component: patientManagement,
                meta: {
                    title: '患者管理',
                    requiresAuth: true
                }
            },
            {
                path: '/effect-prediction',
                name: 'effectPrediction',
                component: effectPrediction,
                meta: {
                    title: '效果预测',
                    requiresAuth: true
                }
            },
            {
                path: '/prediction-records',
                name: 'predictionRecords',
                component: predictionRecords,
                meta: {
                    title: '预测记录',
                    requiresAuth: true
                }
            },
            {
                path: '/doctor-profile',
                name: 'doctorProfile',
                component: doctorProfile,
                meta: {
                    title: '个人信息',
                    requiresAuth: true
                }
            }
        ]
    }
];

const router = createRouter({
    history: createWebHistory(),
    routes: routers
});

// 路由守卫
router.beforeEach((to, from, next) => {
    if (to.matched.length === 0) {
        next('/login');
    } else if (to.meta.requiresAuth) {
        const token = localStorage.getItem('access_token');
        if (!token) {
            next('/login');
        } else {
            next();
        }
    } else {
        next();
    }
});

export { router };


