import { createRouter, createWebHistory } from 'vue-router'
import { resourceList } from './config/resources'

const resourceRoutes = resourceList.flatMap((config) => [
  {
    path: `/${config.api}`,
    name: `${config.key}-list`,
    component: () => import('./views/ResourceList.vue'),
    props: { resourceKey: config.key },
    meta: { title: config.title, requiresAuth: true },
  },
  {
    path: `/${config.api}/new`,
    name: `${config.key}-new`,
    component: () => import('./views/ResourceForm.vue'),
    props: { resourceKey: config.key },
    meta: { title: `新增${config.title}`, requiresAuth: true },
  },
  {
    path: `/${config.api}/:id/edit`,
    name: `${config.key}-edit`,
    component: () => import('./views/ResourceForm.vue'),
    props: { resourceKey: config.key },
    meta: { title: `编辑${config.title}`, requiresAuth: true },
  },
])

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('./views/Login.vue'),
      meta: { title: '登录' },
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('./views/Register.vue'),
      meta: { title: '注册' },
    },
    {
      path: '/',
      name: 'home',
      component: () => import('./views/Home.vue'),
      meta: { title: '工作台', requiresAuth: true },
    },
    ...resourceRoutes,
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})

router.beforeEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} - 药店管理系统` : '药店管理系统'
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) return '/login'
  if (to.path === '/login' && token) return '/'
  return true
})

export default router
