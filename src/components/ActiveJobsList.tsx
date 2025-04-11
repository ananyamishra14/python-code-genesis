
import React from 'react';
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Card, CardContent } from "@/components/ui/card";

// Mock data for active jobs
const MOCK_JOBS = [
  {
    id: "job-001",
    title: "Get 10K legit website visitors",
    status: "in-progress",
    progress: 65,
    budget: 750,
    submittedDate: "2025-03-28",
    expectedCompletionDate: "2025-04-15",
    tasks: 8,
    tasksCompleted: 5
  },
  {
    id: "job-002",
    title: "Build email marketing list of 5K subscribers",
    status: "planning",
    progress: 15,
    budget: 1200,
    submittedDate: "2025-04-02",
    expectedCompletionDate: "2025-05-01",
    tasks: 12,
    tasksCompleted: 2
  },
  {
    id: "job-003",
    title: "Create content for new product launch",
    status: "completed",
    progress: 100,
    budget: 950,
    submittedDate: "2025-02-15",
    expectedCompletionDate: "2025-03-15",
    tasks: 10,
    tasksCompleted: 10
  }
];

const ActiveJobsList = () => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'planning': return 'bg-yellow-100 text-yellow-800';
      case 'in-progress': return 'bg-blue-100 text-blue-800';
      case 'completed': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'planning': return 'Planning';
      case 'in-progress': return 'In Progress';
      case 'completed': return 'Completed';
      default: return 'Unknown';
    }
  };

  return (
    <div className="space-y-4">
      {MOCK_JOBS.length === 0 ? (
        <div className="text-center py-10">
          <p className="text-gray-500">You don't have any active jobs yet.</p>
        </div>
      ) : (
        MOCK_JOBS.map(job => (
          <Card key={job.id} className="hover:shadow-md transition-shadow">
            <CardContent className="p-4">
              <div className="flex flex-col md:flex-row md:items-center md:justify-between">
                <div className="mb-2 md:mb-0">
                  <h3 className="font-medium">{job.title}</h3>
                  <div className="flex items-center mt-1 space-x-2">
                    <Badge className={getStatusColor(job.status)}>
                      {getStatusText(job.status)}
                    </Badge>
                    <span className="text-sm text-gray-500">
                      Submitted: {job.submittedDate}
                    </span>
                  </div>
                </div>
                <div className="text-right">
                  <span className="font-semibold">${job.budget}</span>
                  <div className="text-sm text-gray-500">
                    Est. completion: {job.expectedCompletionDate}
                  </div>
                </div>
              </div>
              
              <div className="mt-4">
                <div className="flex justify-between mb-1">
                  <span className="text-sm">Progress</span>
                  <span className="text-sm font-medium">{job.progress}%</span>
                </div>
                <Progress value={job.progress} className="h-2" />
              </div>
              
              <div className="mt-3 text-sm text-gray-600">
                {job.tasksCompleted} of {job.tasks} tasks completed
              </div>
            </CardContent>
          </Card>
        ))
      )}
    </div>
  );
};

export default ActiveJobsList;
