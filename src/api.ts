import { emails, initialReminders } from './data'
import type { Account, Email, Reminder } from './types'
const base='http://127.0.0.1:8000/api'
async function safe<T>(path:string,fallback:T,init?:RequestInit):Promise<T>{try{const r=await fetch(base+path,init);if(!r.ok)throw new Error();return await r.json()}catch{return fallback}}
export const api={
  emails:(accountId?:string)=>safe<Email[]>(`/emails${accountId?`?account_id=${encodeURIComponent(accountId)}`:''}`,emails),
  accounts:()=>safe<Account[]>('/accounts',[]),
  connect:()=>safe<{authorizationUrl:string}>('/auth/google/start',{authorizationUrl:''}),
  reminders:()=>safe<Reminder[]>('/reminders',initialReminders),
  draft:(id:string,tone:string)=>safe<{draft:string}>(`/emails/${id}/draft?tone=${tone}`,{draft:`Hi,\n\nThank you for reaching out. This sounds good — I'll review the details and get back to you shortly.\n\nBest,\nAditya`},{method:'POST'}),
  send:(email:Email,body:string)=>safe(`/emails/${email.id}/send`,{status:'approved',message:'Reply approved in demo mode'},{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({body,account_id:email.accountId,to:email.email,subject:email.subject,thread_id:email.threadId,message_id:email.messageId})}),
  remind:(emailId:string,when:string)=>safe<Reminder>('/reminders',{id:crypto.randomUUID(),emailId,title:'Follow up reminder',when,status:'scheduled'},{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email_id:emailId,when})})
}
