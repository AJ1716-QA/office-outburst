const CACHE="office-outburst-shell-v3";
const ENGINE="https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js";
const SHELL=["./","./index.html","./manifest.webmanifest","./icon.svg"];
self.addEventListener("install",event=>{
  event.waitUntil((async()=>{
    const cache=await caches.open(CACHE);
    await cache.addAll(SHELL);
    try{await cache.add(ENGINE)}catch(error){console.warn("3D engine could not be cached yet",error)}
    await self.skipWaiting();
  })());
});
self.addEventListener("activate",event=>{
  event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(key=>key!==CACHE).map(key=>caches.delete(key)))).then(()=>self.clients.claim()));
});
self.addEventListener("fetch",event=>{
  const url=new URL(event.request.url);
  const isEngine=url.href===ENGINE;
  if(event.request.method!=="GET"||(!isEngine&&url.origin!==self.location.origin))return;
  event.respondWith((async()=>{
    const cache=await caches.open(CACHE);
    const cached=await cache.match(event.request);
    if(cached)return cached;
    try{
      const response=await fetch(event.request);
      if(response.ok||response.type==="opaque")await cache.put(event.request,response.clone());
      return response;
    }catch(error){
      if(!isEngine)return (await cache.match("./index.html"));
      throw error;
    }
  })());
});