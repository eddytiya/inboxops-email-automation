export interface Account{id:string;email:string;name?:string;picture?:string}
export interface Attachment{id:string;filename:string;mimeType:string;size:number}
export interface Message{id:string;accountId:string;threadId:string;messageId?:string;from:string;to:string;cc:string;subject:string;date:string;snippet:string;bodyText:string;bodyHtml:string;attachments:Attachment[];labels:string[];unread:boolean;starred:boolean;messageCount?:number}
export interface Thread{id:string;accountId:string;messages:Message[]}
export interface Compose{account_id:string;to:string;subject:string;body:string;cc?:string;bcc?:string;thread_id?:string;reply_to_id?:string;idempotency_key?:string}
export interface SmartSection{id:string;name:string;gmailLabel:string;labelId?:string;count:number}
export interface SmartSectionSync{classified:number;assignments:{threadId:string;topic:string;labelId:string;confidence:number;reason:string}[];sections:SmartSection[];localOnly:boolean}
const BASE='http://127.0.0.1:8000/api';
async function request<T>(path:string,init?:RequestInit):Promise<T>{const r=await fetch(BASE+path,init);if(!r.ok){let message=`Request failed (${r.status})`;try{message=(await r.json()).detail||message}catch{}throw new Error(message)}return r.status===204?undefined as T:r.json()}
const json=(method:string,body:unknown):RequestInit=>({method,headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
export const gmailApi={
 accounts:()=>request<Account[]>('/accounts'),
 connect:()=>request<{authorizationUrl:string}>('/auth/google/start'),
 disconnect:(id:string)=>request(`/accounts/${id}`,{method:'DELETE'}),
 threads:(accountId:string,token?:string,q?:string)=>request<{items:Message[];nextPageToken?:string}>(`/gmail/threads?account_id=${encodeURIComponent(accountId)}${token?`&page_token=${encodeURIComponent(token)}`:''}${q?`&q=${encodeURIComponent(q)}`:''}`),
 thread:(accountId:string,id:string)=>request<Thread>(`/gmail/threads/${id}?account_id=${encodeURIComponent(accountId)}`),
 labels:(accountId:string)=>request<{id:string;name:string;type:string}[]>(`/gmail/labels?account_id=${encodeURIComponent(accountId)}`),
 smartSectionCatalog:()=>request<{id:string;name:string}[]>('/smart-sections/catalog'),
 smartSections:(accountId:string,selected:string[]=[])=>request<SmartSection[]>(`/smart-sections?account_id=${encodeURIComponent(accountId)}${selected.length?`&selected=${encodeURIComponent(selected.join(','))}`:''}`),
 syncSmartSections:(accountId:string,selected:string[],limit=50)=>request<SmartSectionSync>(`/smart-sections/sync?account_id=${encodeURIComponent(accountId)}&limit=${limit}&selected=${encodeURIComponent(selected.join(','))}`,{method:'POST'}),
 modify:(m:Message,add:string[]=[],remove:string[]=[])=>request(`/gmail/threads/${m.threadId}/labels?account_id=${encodeURIComponent(m.accountId)}`,json('PATCH',{add,remove})),
 draft:(data:Compose)=>request<{id:string}>('/gmail/drafts',json('POST',data)),
 send:(data:Compose)=>request<{id:string;duplicatePrevented:boolean}>('/gmail/send',json('POST',data)),
 remind:(data:{title:string;remind_at:string;account_id?:string;thread_id?:string;condition_type?:string})=>request('/operations/reminders',json('POST',data)),
 dueReminders:()=>request<{id:string;title:string;remind_at:string}[]>('/operations/reminders/due'),
 completeReminder:(id:string)=>request(`/operations/reminders/${id}/complete`,{method:'POST'}),
 analyze:(message:Message)=>request<{category:string;priority:number;priorityReason:string;summary:string;actionRequired:string;entities:Record<string,string[]>;tasks:{task:string;deadline?:string}[];waitingOn:string;confidence:number;model?:string;provider?:string;privacy?:{redacted:boolean;types:string[]}} >('/intelligence/analyze',json('POST',{account_id:message.accountId,subject:message.subject,body:message.bodyText,sender:message.from,date:message.date})),
 intelligentDraft:(message:Message,tone:string,instruction?:string)=>request<{draft:string;requiresApproval:boolean}>('/intelligence/draft',json('POST',{account_id:message.accountId,subject:message.subject,body:message.bodyText,sender:message.from,date:message.date,tone,instruction})),
 dailyBrief:(accountId:string)=>request<{headline:string;summary:string;urgentCount:number;replyCount:number;estimatedMinutes:number;priorities:{threadId:string;subject:string;sender:string;priority:number;reason:string}[];model:string}>(`/intelligence/daily-brief?account_id=${encodeURIComponent(accountId)}`),
 followup:(data:{account_id:string;thread_id:string;subject:string;due_at:string})=>request('/operations/followups',json('POST',data)),
 checkFollowups:()=>request<{id:string;subject:string;due_at:string}[]>('/operations/followups/check'),
 notifications:(unreadOnly=true)=>request<{id:string;kind:string;title:string;body:string;status:string}[]>(`/notifications?unread_only=${unreadOnly}`),
 readNotification:(id:string)=>request(`/notifications/${id}/read`,{method:'POST'}),
 attachmentUrl:(m:Message,a:Attachment)=>`${BASE}/gmail/messages/${m.id}/attachments/${a.id}?account_id=${encodeURIComponent(m.accountId)}&filename=${encodeURIComponent(a.filename)}`
}

export const workspaceApi={
 privacy:()=>request<any>('/privacy'),privacySave:(x:any)=>request('/privacy',json('PUT',x)),audit:()=>request<any[]>('/privacy/audit'),
 index:(accountId:string)=>request<{indexed:number}>(`/search/index?account_id=${encodeURIComponent(accountId)}`,{method:'POST'}),search:(q:string,accountId='all')=>request<any[]>(`/search?q=${encodeURIComponent(q)}&account_id=${encodeURIComponent(accountId)}`),
 tasks:()=>request<any[]>('/tasks'),taskCreate:(x:any)=>request<any>('/tasks',json('POST',x)),taskUpdate:(id:string,x:any)=>request<any>(`/tasks/${id}`,json('PATCH',x)),
 contacts:()=>request<any[]>('/contacts'),contactUpdate:(email:string,x:any)=>request<any>(`/contacts/${encodeURIComponent(email)}`,json('PATCH',x)),
 profile:(accountId:string)=>request<any>(`/writing-profile/${accountId}`),profileSave:(accountId:string,x:any)=>request<any>(`/writing-profile/${accountId}`,json('PUT',x))
 ,calendarStatus:(accountId:string)=>request<any>(`/calendar/status/${accountId}`),calendarConnect:()=>request<{authorizationUrl:string}>('/auth/google/calendar/start'),calendarEvent:(x:any)=>request<any>('/calendar/events',json('POST',x)),
 attachmentText:(m:Message,a:Attachment)=>request<any>(`/gmail/messages/${m.id}/attachments/${a.id}/text?account_id=${encodeURIComponent(m.accountId)}&mime_type=${encodeURIComponent(a.mimeType)}&filename=${encodeURIComponent(a.filename)}`)
}
