import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { message } from 'antd';
import * as courseService from '@/services/courseService';

export function useCourses(filters?: courseService.CourseFilters) {
  return useQuery({
    queryKey: ['courses', filters],
    queryFn: () => courseService.getCourses(filters).then((r) => r.data),
  });
}

export function useCourse(id?: string) {
  return useQuery({
    queryKey: ['course', id],
    queryFn: () => courseService.getCourse(id!).then((r) => r.data),
    enabled: !!id,
  });
}

export function useCreateCourse() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Parameters<typeof courseService.createCourse>[0]) =>
      courseService.createCourse(data).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['courses'] });
      message.success('Tạo học phần thành công');
    },
    onError: () => message.error('Không thể tạo học phần'),
  });
}

export function useUpdateCourse() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Parameters<typeof courseService.updateCourse>[1] }) =>
      courseService.updateCourse(id, data).then((r) => r.data),
    onSuccess: (_d, vars) => {
      qc.invalidateQueries({ queryKey: ['courses'] });
      qc.invalidateQueries({ queryKey: ['course', vars.id] });
      message.success('Cập nhật học phần thành công');
    },
    onError: () => message.error('Không thể cập nhật học phần'),
  });
}

export function useCourseGroups(filters?: courseService.CourseGroupFilters) {
  return useQuery({
    queryKey: ['course-groups', filters],
    queryFn: () => courseService.getCourseGroups(filters).then((r) => r.data),
  });
}
