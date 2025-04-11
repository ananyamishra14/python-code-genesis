
import React, { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { useToast } from "@/components/ui/use-toast";

// Mock data for tasks
const MOCK_TASKS = [
  {
    id: "task-001",
    title: "Write 5 SEO-optimized blog posts about digital marketing",
    description: "Create 5 high-quality blog posts (1500+ words each) targeting keywords related to digital marketing...",
    budget: 250,
    timeline: "7 days",
    skills: ["Content Writing", "SEO", "Marketing"],
    difficulty: "medium",
    mainJobTitle: "Get 10K legit website visitors"
  },
  {
    id: "task-002",
    title: "Setup Google Analytics and Tag Manager",
    description: "Install and configure Google Analytics 4 and Google Tag Manager on a WordPress website...",
    budget: 100,
    timeline: "2 days",
    skills: ["Google Analytics", "WordPress", "Web Development"],
    difficulty: "easy",
    mainJobTitle: "Get 10K legit website visitors"
  },
  {
    id: "task-003",
    title: "Optimize website loading speed",
    description: "Improve website loading time to achieve at least 90 score on Google PageSpeed Insights...",
    budget: 180,
    timeline: "4 days",
    skills: ["Web Performance", "Front-end Development"],
    difficulty: "hard",
    mainJobTitle: "Get 10K legit website visitors"
  },
  {
    id: "task-004",
    title: "Design 10 social media graphics for product launch",
    description: "Create 10 eye-catching social media graphics in various formats for Facebook, Instagram, and Twitter...",
    budget: 120,
    timeline: "5 days",
    skills: ["Graphic Design", "Social Media"],
    difficulty: "medium",
    mainJobTitle: "Create content for new product launch"
  },
];

const TaskBoard = () => {
  const { toast } = useToast();
  const [appliedTasks, setAppliedTasks] = useState<string[]>([]);
  
  const handleApply = (taskId: string) => {
    setAppliedTasks(prev => [...prev, taskId]);
    toast({
      title: "Application submitted!",
      description: "You'll be notified if you're selected for this task.",
    });
  };
  
  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'hard': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div>
      <Tabs defaultValue="all">
        <TabsList className="mb-6">
          <TabsTrigger value="all">All Tasks</TabsTrigger>
          <TabsTrigger value="matched">Matched for You</TabsTrigger>
          <TabsTrigger value="applied">Applied</TabsTrigger>
        </TabsList>
        
        <TabsContent value="all" className="space-y-4">
          {MOCK_TASKS.map(task => (
            <Card key={task.id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-4 pt-6">
                <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between">
                  <div className="flex-1">
                    <h3 className="font-medium text-lg">{task.title}</h3>
                    <p className="text-sm text-gray-600 mt-1">
                      Part of: {task.mainJobTitle}
                    </p>
                    <p className="mt-3 text-gray-700">
                      {task.description}
                    </p>
                    
                    <div className="mt-4 flex flex-wrap gap-2">
                      {task.skills.map((skill, index) => (
                        <Badge key={index} variant="outline" className="bg-indigo-50">
                          {skill}
                        </Badge>
                      ))}
                      
                      <Badge className={getDifficultyColor(task.difficulty)}>
                        {task.difficulty.charAt(0).toUpperCase() + task.difficulty.slice(1)}
                      </Badge>
                    </div>
                  </div>
                  
                  <div className="mt-4 lg:mt-0 lg:ml-6 lg:text-right flex flex-col items-start lg:items-end">
                    <div className="text-lg font-semibold">${task.budget}</div>
                    <div className="text-sm text-gray-600 mb-4">
                      Timeline: {task.timeline}
                    </div>
                  </div>
                </div>
              </CardContent>
              
              <CardFooter className="bg-gray-50 p-4">
                <Button 
                  onClick={() => handleApply(task.id)} 
                  disabled={appliedTasks.includes(task.id)}
                  className="w-full sm:w-auto"
                >
                  {appliedTasks.includes(task.id) ? 'Applied' : 'Apply for this Task'}
                </Button>
              </CardFooter>
            </Card>
          ))}
        </TabsContent>
        
        <TabsContent value="matched">
          <div className="text-center py-10">
            <p className="text-gray-500">
              Tasks that match your skills and preferences will appear here.
            </p>
            <p className="text-gray-500 mt-2">
              Complete your profile to get better matches.
            </p>
          </div>
        </TabsContent>
        
        <TabsContent value="applied" className="space-y-4">
          {appliedTasks.length === 0 ? (
            <div className="text-center py-10">
              <p className="text-gray-500">You haven't applied for any tasks yet.</p>
            </div>
          ) : (
            MOCK_TASKS
              .filter(task => appliedTasks.includes(task.id))
              .map(task => (
                <Card key={task.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-4 pt-6">
                    <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between">
                      <div className="flex-1">
                        <h3 className="font-medium text-lg">{task.title}</h3>
                        <p className="text-sm text-gray-600 mt-1">
                          Part of: {task.mainJobTitle}
                        </p>
                        <p className="mt-3 text-gray-700">
                          {task.description}
                        </p>
                        
                        <div className="mt-4 flex flex-wrap gap-2">
                          {task.skills.map((skill, index) => (
                            <Badge key={index} variant="outline" className="bg-indigo-50">
                              {skill}
                            </Badge>
                          ))}
                          
                          <Badge className={getDifficultyColor(task.difficulty)}>
                            {task.difficulty.charAt(0).toUpperCase() + task.difficulty.slice(1)}
                          </Badge>
                        </div>
                      </div>
                      
                      <div className="mt-4 lg:mt-0 lg:ml-6 lg:text-right flex flex-col items-start lg:items-end">
                        <div className="text-lg font-semibold">${task.budget}</div>
                        <div className="text-sm text-gray-600 mb-4">
                          Timeline: {task.timeline}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                  
                  <CardFooter className="bg-gray-50 p-4">
                    <Badge className="bg-blue-100 text-blue-800">
                      Application Under Review
                    </Badge>
                  </CardFooter>
                </Card>
              ))
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default TaskBoard;
