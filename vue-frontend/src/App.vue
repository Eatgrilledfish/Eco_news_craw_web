<template>
  <el-container class="home-container">
    <!-- Header Section -->
    <el-header class="header">
      <el-menu :default-active="activeIndex" class="menu-demo" mode="horizontal" @select="handleSelect">
        <el-menu-item index="1">首页</el-menu-item>
        <el-menu-item index="2">新闻</el-menu-item>
        <el-menu-item index="3">热点分析</el-menu-item>
        <el-menu-item index="4">搜索</el-menu-item>
      </el-menu>
    </el-header>

    <!-- Main Content -->
    <el-main class="main-content">
      <div class="stats-container">
        <!-- News Count Card -->
        <el-card class="stat-card">
          <div slot="header" class="card-header">
            <span>新闻总数<br>News count</span>
          </div>
          <div class="card-content">
            <div>{{ newsCount }} </div>
          </div>
        </el-card>

        <!-- Words Count Card -->
        <el-card class="stat-card">
          <div slot="header" class="card-header">
            <span>词总计<br>Words count</span>
          </div>
          <div class="card-content">
            <div>{{ wordsCount }}</div>
          </div>
        </el-card>
      </div>
    </el-main>
  </el-container>
</template>

<script lang="ts">
import axios from 'axios';
import { defineComponent, ref, onMounted } from 'vue';

export default defineComponent({
  setup() {
    const activeIndex = ref('1');
    const newsCount = ref(0); // 响应式引用
    const wordsCount = ref(2); // 响应式引用

    const handleSelect = (key: string, keypath: string[]) => {
      activeIndex.value = key;
    };

    const fetchNewsHome = () => {
      axios.get('http://127.0.0.1:5000/news/home')
        .then(response => {
          newsCount.value = response.data.newsCount
          wordsCount.value = response.data.wordsCount
        })
        .catch(error => {
          console.error("There was an error!", error);
        });
    };

    onMounted(() => {
      fetchNewsHome();
    });

    return {
      activeIndex,
      newsCount,
      wordsCount,
      handleSelect,
      fetchNewsHome
    };
  },
});
</script>


<style >
body {
  background-color: white; /* This sets the background color of the entire page */
}

.home-container {
  display: flex; /* Use flexbox layout to facilitate inner content alignment */
  justify-content: center; /* Center children horizontally */
  align-items: center; /* Center children vertically */
  flex-direction: column; /* Stack children vertically */
  width: 100vw; /* Set the width to 100% of the viewport width */
  min-height: 100vh; /* Set the minimum height to 100% of the viewport height */
  margin: 0; /* Remove default margin */
  padding: 0; /* Remove default padding */
  background-color: white; /* Set the background color to white */
  box-sizing: border-box; /* Make sure padding and border are included in the total width and height */
}

.header {
  background-color: #b3c0d1;
  color: white;
  width: 420px;
  line-height: 60px;
}

.menu-demo {
  /* Additional menu styles if needed */
}

.main-content {
  /* Additional main content styles if needed */
}

.stats-container {
  text-align: center;
}

.stat-card {
  width: 300px;
  margin: 20px;
  display: inline-block;
}

.card-header {
  /* Additional card header styles if needed */
}

.card-content {
  /* Additional card content styles if needed */
}

/* ...additional styles... */
</style>