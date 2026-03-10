import os
import glob

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    new_lines = []
    
    for line in lines:
        if line.startswith('from unfold.admin import'):
            continue
        new_lines.append(line)

    new_content = '\n'.join(new_lines)

    new_content = new_content.replace('class ImportTaskAdmin(ModelAdmin):', 'class ImportTaskAdmin(admin.ModelAdmin):')
    new_content = new_content.replace('class TrainingProgramAdmin(ModelAdmin):', 'class TrainingProgramAdmin(admin.ModelAdmin):')
    new_content = new_content.replace('class ProgramObjectiveAdmin(ProgramContextMixin, ModelAdmin):', 'class ProgramObjectiveAdmin(ProgramContextMixin, admin.ModelAdmin):')
    new_content = new_content.replace('class PLOAdmin(ProgramContextMixin, ModelAdmin):', 'class PLOAdmin(ProgramContextMixin, admin.ModelAdmin):')
    new_content = new_content.replace('class PIAdmin(ProgramContextMixin, ModelAdmin):', 'class PIAdmin(ProgramContextMixin, admin.ModelAdmin):')
    new_content = new_content.replace('class CourseGroupAdmin(ProgramContextMixin, ModelAdmin):', 'class CourseGroupAdmin(ProgramContextMixin, admin.ModelAdmin):')
    new_content = new_content.replace('class KnowledgeBlockAdmin(ProgramContextMixin, ModelAdmin):', 'class KnowledgeBlockAdmin(ProgramContextMixin, admin.ModelAdmin):')
    new_content = new_content.replace('class CourseAdmin(ModelAdmin):', 'class CourseAdmin(admin.ModelAdmin):')
    new_content = new_content.replace('class ProgramCourseAdmin(ProgramContextMixin, ModelAdmin):', 'class ProgramCourseAdmin(ProgramContextMixin, admin.ModelAdmin):')
    new_content = new_content.replace('class SemesterPlanAdmin(ProgramContextMixin, ModelAdmin):', 'class SemesterPlanAdmin(ProgramContextMixin, admin.ModelAdmin):')
    new_content = new_content.replace('class CoursePLOContributionAdmin(ProgramContextMixin, ModelAdmin):', 'class CoursePLOContributionAdmin(ProgramContextMixin, admin.ModelAdmin):')
    new_content = new_content.replace('class PLOAssessmentPlanAdmin(ProgramContextMixin, ModelAdmin):', 'class PLOAssessmentPlanAdmin(ProgramContextMixin, admin.ModelAdmin):')
    
    new_content = new_content.replace('class NotificationAdmin(ModelAdmin):', 'class NotificationAdmin(admin.ModelAdmin):')

    new_content = new_content.replace('class DepartmentAdmin(ModelAdmin):', 'class DepartmentAdmin(admin.ModelAdmin):')
    new_content = new_content.replace('class RoleAdmin(ModelAdmin):', 'class RoleAdmin(admin.ModelAdmin):')
    new_content = new_content.replace('class PermissionAdmin(ModelAdmin):', 'class PermissionAdmin(admin.ModelAdmin):')
    new_content = new_content.replace('class UserRoleAdmin(ModelAdmin):', 'class UserRoleAdmin(admin.ModelAdmin):')
    new_content = new_content.replace('class AuditLogAdmin(ModelAdmin):', 'class AuditLogAdmin(admin.ModelAdmin):')
    
    new_content = new_content.replace('class ApprovalWorkflowAdmin(ModelAdmin):', 'class ApprovalWorkflowAdmin(admin.ModelAdmin):')
    new_content = new_content.replace('class EntityVersionAdmin(ModelAdmin):', 'class EntityVersionAdmin(admin.ModelAdmin):')
    new_content = new_content.replace('class ApprovalCommentAdmin(ModelAdmin):', 'class ApprovalCommentAdmin(admin.ModelAdmin):')

    new_content = new_content.replace('class UserAdmin(auth_admin.UserAdmin, ModelAdmin):', 'class UserAdmin(auth_admin.UserAdmin):')
    
    new_content = new_content.replace('(TabularInline)', '(admin.TabularInline)')
    new_content = new_content.replace('(StackedInline)', '(admin.StackedInline)')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

for admin_file in glob.glob('hutech_program/**/admin.py', recursive=True):
    process_file(admin_file)
    print(f"Reverted {admin_file}")

