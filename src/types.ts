export type Category = 'Urgent'|'Requires reply'|'Follow-up'|'Meeting'|'Invoice'|'Newsletter'
export interface ActionItem { task:string; deadline?:string; owner:string }
export interface Email { id:string; accountId?:string; threadId?:string; messageId?:string; sender:string; email:string; initials:string; subject:string; preview:string; body:string; receivedAt:string; relativeTime:string; category:Category; priority:number; unread:boolean; starred:boolean; summary:string; actionRequired:string; reason:string; people:string[]; attachments:string[]; actionItems:ActionItem[]; threadCount:number; waitingDays?:number }
export interface Reminder { id:string; emailId:string; title:string; when:string; status:'scheduled'|'done' }
export interface Account { id:string; email:string; name?:string; picture?:string; connected_at:string }
