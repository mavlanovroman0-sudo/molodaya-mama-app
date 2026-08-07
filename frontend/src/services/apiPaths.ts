/** Единый реестр путей API — должен совпадать с роутерами backend/app/main.py */

export const API_PATHS = {
  auth: {
    login: '/api/v1/auth/login',
    register: '/api/v1/auth/register',
    me: '/api/v1/auth/me',
  },
  shopping: {
    lists: '/api/v1/shopping/lists',
    items: (listId: string) => `/api/v1/shopping/items/${listId}`,
    createItem: '/api/v1/shopping/items',
    updateItem: (itemId: string) => `/api/v1/shopping/items/${itemId}`,
  },
  barter: {
    ads: '/api/v1/barter/ads',
    adRequest: (adId: string) => `/api/v1/barter/ads/${adId}/request`,
  },
  tasks: {
    list: '/api/v1/tasks',
    logs: '/api/v1/task_logs',
    report: '/api/v1/task_logs/report',
  },
  smartHome: {
    devices: '/api/v1/devices',
    device: (id: string) => `/api/v1/devices/${id}`,
    scenarios: '/api/v1/scenarios',
    runScenario: (id: string) => `/api/v1/scenarios/${id}/run`,
  },
  baby: {
    feeds: '/api/v1/baby/feeds',
    sleep: '/api/v1/baby/sleep',
    sleepItem: (id: string) => `/api/v1/baby/sleep/${id}`,
    diapers: '/api/v1/baby/diapers',
    checklist: '/api/v1/baby/checklist',
    checklistItem: (id: string) => `/api/v1/baby/checklist/${id}`,
  },
  subscription: {
    status: '/api/v1/user/subscription-status',
    prices: '/api/v1/subscription/prices',
    checkout: '/api/v1/subscription/checkout',
    verify: '/api/v1/subscription/verify',
    cancel: '/api/v1/subscription/cancel',
  },
  user: {
    location: '/api/v1/user/location',
    nanny: '/api/v1/user/nanny',
    nannies: '/api/v1/nannies',
    nannyRequest: '/api/v1/nannies/request',
    subscriptionStatus: '/api/v1/user/subscription-status',
  },
  roles: {
    switch: '/api/v1/roles/switch',
  },
  referral: {
    stats: '/api/v1/referral/stats',
  },
  config: {
    remote: '/api/v1/config/remote',
  },
  geo: {
    detect: '/api/v1/geo/detect',
  },
} as const;
