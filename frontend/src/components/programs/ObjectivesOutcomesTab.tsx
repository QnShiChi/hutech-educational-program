import { Divider, Spin } from 'antd';

import EditableList from './EditableList';
import CheckboxMatrix from './CheckboxMatrix';
import {
  useObjectives,
  useCreateObjective,
  useUpdateObjective,
  useDeleteObjective,
  useReorderObjectives,
  usePLOs,
  useCreatePLO,
  useUpdatePLO,
  useDeletePLO,
  useReorderPLOs,
  usePOPLOMatrix,
  useUpdatePOPLOMatrix,
} from '@/hooks/useProgramDetail';

interface Props {
  programId: string;
}

export default function ObjectivesOutcomesTab({ programId }: Props) {
  const { data: objectives, isLoading: loadingPO } = useObjectives(programId);
  const createObj = useCreateObjective(programId);
  const updateObj = useUpdateObjective(programId);
  const deleteObj = useDeleteObjective(programId);
  const reorderObj = useReorderObjectives(programId);

  const { data: plos, isLoading: loadingPLO } = usePLOs(programId);
  const createPLO = useCreatePLO(programId);
  const updatePLO = useUpdatePLO(programId);
  const deletePLO = useDeletePLO(programId);
  const reorderPLO = useReorderPLOs(programId);

  const { data: matrixData, isLoading: loadingMatrix } = usePOPLOMatrix(programId);
  const updateMatrix = useUpdatePOPLOMatrix(programId);

  if (loadingPO || loadingPLO || loadingMatrix) return <Spin className="flex justify-center mt-10" />;

  return (
    <div>
      <EditableList
        title="Mục tiêu chương trình (PO)"
        items={(objectives ?? []).map((o) => ({ id: o.id, code: o.code, description: o.description, order: o.order }))}
        onCreate={async (data) => { await createObj.mutateAsync(data); }}
        onUpdate={async (id, data) => { await updateObj.mutateAsync({ id, data }); }}
        onDelete={async (id) => { await deleteObj.mutateAsync(id); }}
        onReorder={async (ids) => { await reorderObj.mutateAsync(ids); }}
        permission="programs.manage_programs"
      />

      <EditableList
        title="Chuẩn đầu ra (PLO)"
        items={(plos ?? []).map((p) => ({ id: p.id, code: p.code, description: p.description, order: p.order, bloom_level: p.bloom_level }))}
        showBloom
        onCreate={async (data) => { await createPLO.mutateAsync(data); }}
        onUpdate={async (id, data) => { await updatePLO.mutateAsync({ id, data }); }}
        onDelete={async (id) => { await deletePLO.mutateAsync(id); }}
        onReorder={async (ids) => { await reorderPLO.mutateAsync(ids); }}
        permission="programs.manage_programs"
      />

      <Divider />

      <CheckboxMatrix
        objectives={objectives ?? []}
        plos={plos ?? []}
        mappings={matrixData?.mappings ?? []}
        onSave={async (mappings) => { await updateMatrix.mutateAsync({ mappings }); }}
      />
    </div>
  );
}
