<template>
    <div class="container">
        <slot class="contained" />
    </div>
</template>

<style scoped>
.container {
    /* border: 1px solid blue; */
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    width: 100%;
}

.contained {
    flex: 1;
    /* border: 1px solid pink; */
}
</style>
