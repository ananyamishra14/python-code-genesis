
import React from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import JobSubmissionForm from '@/components/JobSubmissionForm';
import ActiveJobsList from '@/components/ActiveJobsList';
import TaskBoard from '@/components/TaskBoard';
import HowItWorks from '@/components/HowItWorks';

const Index = () => {
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-indigo-50">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-12">
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
            Job-to-Be-Done Marketplace
          </h1>
          <p className="text-xl md:text-2xl text-gray-600 max-w-3xl mx-auto mb-8">
            Submit your problems, not job postings. Our AI decomposes tasks, sources solutions, and manages micro-contractors for you.
          </p>
          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <Button size="lg" className="bg-indigo-600 hover:bg-indigo-700">
              Submit a Problem
            </Button>
            <Button size="lg" variant="outline" className="border-indigo-600 text-indigo-600">
              Become a Solver
            </Button>
          </div>
        </div>

        {/* How It Works Section */}
        <HowItWorks />

        {/* Main Dashboard */}
        <div className="mt-16">
          <Tabs defaultValue="submit" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="submit">Submit Problem</TabsTrigger>
              <TabsTrigger value="active">Active Jobs</TabsTrigger>
              <TabsTrigger value="tasks">Task Board</TabsTrigger>
            </TabsList>
            
            <TabsContent value="submit">
              <Card>
                <CardHeader>
                  <CardTitle>Submit Your Problem</CardTitle>
                  <CardDescription>
                    Tell us what you need done, and we'll handle the rest
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <JobSubmissionForm />
                </CardContent>
              </Card>
            </TabsContent>
            
            <TabsContent value="active">
              <Card>
                <CardHeader>
                  <CardTitle>Your Active Jobs</CardTitle>
                  <CardDescription>
                    Track the progress of your submitted problems
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ActiveJobsList />
                </CardContent>
              </Card>
            </TabsContent>
            
            <TabsContent value="tasks">
              <Card>
                <CardHeader>
                  <CardTitle>Task Board</CardTitle>
                  <CardDescription>
                    Available micro-tasks for solvers
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <TaskBoard />
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
};

export default Index;
