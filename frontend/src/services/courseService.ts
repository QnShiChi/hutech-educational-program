import apiClient from '@/services/apiClient';
import type { PaginatedResponse, Course, CourseGroup } from '@/types/api';

/* ─── Query params ─── */
export interface CourseFilters {
  search?: string;
  course_type?: string;
  page?: number;
  page_size?: number;
}

export interface CourseGroupFilters {
  search?: string;
  page?: number;
  page_size?: number;
}

/* ─── Courses ─── */
export const getCourses = (params?: CourseFilters) =>
  apiClient.get<PaginatedResponse<Course>>('/courses/', { params });

export const getCourse = (id: string) =>
  apiClient.get<Course>(`/courses/${id}/`);

export const createCourse = (data: Partial<Course>) =>
  apiClient.post<Course>('/courses/', data);

export const updateCourse = (id: string, data: Partial<Course>) =>
  apiClient.put<Course>(`/courses/${id}/`, data);

/* ─── Course Groups ─── */
export const getCourseGroups = (params?: CourseGroupFilters) =>
  apiClient.get<PaginatedResponse<CourseGroup>>('/course-groups/', { params });
