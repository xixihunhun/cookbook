/** 通用 API 响应 */
export interface ApiResponse<T = unknown> {
  code: number;
  msg: string;
  data: T;
}

/** 分页数据 */
export interface Paginated<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

/** 用户 */
export interface User {
  id: number;
  username: string;
  nickname?: string;
  avatar?: string | null;
  bio?: string | null;
}

/** 菜谱 */
export interface Recipe {
  id: number;
  title: string;
  material: string;
  step: string;
  tip?: string;
  cover_img?: string;
  is_collect?: boolean;
  category_id?: number | null;
  category_name?: string | null;
  cook_time?: string;
  author_id?: number;
  author_name?: string | null;
  views: number;
  created_at?: string;
  updated_at?: string;
}

/** 分类 */
export interface Category {
  id: number;
  name: string;
}

/** 家庭成员 */
export interface FamilyMember {
  id: number;
  user_id: number;
  nickname: string;
  avatar?: string | null;
  is_creator: boolean;
}

/** 家庭 */
export interface Family {
  id: number;
  name: string;
  invite_code: string;
  creator_id: number;
  members: FamilyMember[];
}

/** 投票 */
export interface VoteRecord {
  id: number;
  user_id: number;
  user_nickname: string;
  recipe_id: number;
  recipe_title: string;
  vote_date: string;
  created_at: string;
}

/** 今日投票结果 */
export interface VoteTodayResult {
  my_vote?: VoteRecord | null;
  partner_vote?: VoteRecord | null;
  agreed: boolean;
  deadline: string;       // ISO 时间
  deadline_ts: number;   // 截止时间戳（秒）
  voted_count: number;   // 已投票人数
}

/** 历史投票 */
export interface VoteHistoryItem {
  vote_date: string;
  winner_recipe?: Recipe | null;
  my_vote?: VoteRecord | null;
  partner_vote?: VoteRecord | null;
  agreed: boolean;
}

/** 微信登录返回 */
export interface WxLoginResult {
  token: string;
  user: User;
  is_new: boolean;
}
