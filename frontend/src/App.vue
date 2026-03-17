<template>
  <div id="app">
    <nav class="navbar">
      <router-link to="/" class="logo">SmartFish</router-link>
      <div class="nav-links">
        <router-link to="/">Home</router-link>
      </div>
    </nav>
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f1117; color: #e0e0e0; }
.navbar { display: flex; align-items: center; padding: 1rem 2rem; background: #1a1d27; border-bottom: 1px solid #2a2d3a; }
.logo { font-size: 1.5rem; font-weight: bold; color: #4fc3f7; text-decoration: none; margin-right: 2rem; }
.nav-links a { color: #9e9e9e; text-decoration: none; margin-right: 1.5rem; transition: color 0.2s; }
.nav-links a:hover, .nav-links a.router-link-active { color: #4fc3f7; }
.main-content { padding: 2rem; max-width: 1400px; margin: 0 auto; }
</style>
