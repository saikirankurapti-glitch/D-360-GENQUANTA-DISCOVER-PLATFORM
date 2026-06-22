import type { Meta, StoryObj } from '@storybook/react';
import { QueryBuilderPage } from '../pages/QueryBuilderPage';
import { ReactFlowProvider } from '@xyflow/react';
import { useQueryBuilderStore } from '../store/useQueryBuilderStore';
import { useEffect } from 'react';

const meta: Meta<typeof QueryBuilderPage> = {
  title: 'Informatics/QueryBuilder',
  component: QueryBuilderPage,
  decorators: [
    (Story) => (
      <ReactFlowProvider>
        <div className="h-screen w-screen p-8 bg-[#070b13] text-white">
          <Story />
        </div>
      </ReactFlowProvider>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof QueryBuilderPage>;

// Helper to pre-populate canvas for Storybook visual review
const TemplateDecorator = ({ children }: { children: React.ReactNode }) => {
  const { addEntityNode, clearCanvas } = useQueryBuilderStore();
  
  useEffect(() => {
    clearCanvas();
    // Seed canvas with compound and assay nodes for demo
    addEntityNode('Compound');
    setTimeout(() => {
      addEntityNode('Assay');
    }, 100);
  }, []);

  return <>{children}</>;
};

export const EmptyCanvas: Story = {};

export const PopulatedCanvas: Story = {
  decorators: [
    (Story) => (
      <TemplateDecorator>
        <Story />
      </TemplateDecorator>
    ),
  ],
};
