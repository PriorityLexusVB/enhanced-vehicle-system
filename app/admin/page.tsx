"use client"

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { onAuthStateChanged, User } from 'firebase/auth';
import { auth } from '@/lib/firebaseconfig';
import { getUserRole, isAdmin, UserRole } from '@/lib/auth-utils';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Sidebar, SidebarContent, SidebarHeader, SidebarMenu, SidebarMenuItem, SidebarMenuButton, SidebarProvider } from "@/components/ui/sidebar";
import { Trash2, UserPlus, Users, Shield, ArrowLeft, Loader2, Settings, BarChart3 } from 'lucide-react';
import { toast } from "@/hooks/use-toast";

interface AppUser {
  uid: string;
  email: string;
  role: string;
  createdAt: string | null;
}

export default function AdminPanel() {
  const router = useRouter();
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [userRole, setUserRole] = useState<UserRole | null>(null);
  const [loading, setLoading] = useState(true);
  const [users, setUsers] = useState<AppUser[]>([]);
  const [loadingUsers, setLoadingUsers] = useState(false);
  const [activeView, setActiveView] = useState<'users' | 'analytics'>('users');
  
  // Add user form state
  const [addUserForm, setAddUserForm] = useState({
    email: '',
    password: '',
    role: ''
  });
  const [addingUser, setAddingUser] = useState(false);
  
  // UI state
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Check authentication and role on mount
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      if (!user) {
        router.push('/?error=Access Denied - Please login first');
        return;
      }

      setCurrentUser(user);
      const role = await getUserRole(user);
      setUserRole(role);

      if (!isAdmin(role)) {
        router.push('/?error=Access Denied - Admin privileges required');
        return;
      }

      setLoading(false);
      fetchUsers();
    });

    return () => unsubscribe();
  }, [router]);

  const fetchUsers = async () => {
    setLoadingUsers(true);
    try {
      const response = await fetch('/api/admin/users');
      const data = await response.json();
      
      if (response.ok) {
        setUsers(data.users);
      } else {
        setError(data.error || 'Failed to fetch users');
        toast({
          title: "Error",
          description: data.error || 'Failed to fetch users',
          variant: "destructive",
        });
      }
    } catch (error) {
      setError('Failed to fetch users');
      toast({
        title: "Error",
        description: 'Failed to fetch users',
        variant: "destructive",
      });
    } finally {
      setLoadingUsers(false);
    }
  };

  const handleAddUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setAddingUser(true);
    setError('');
    setSuccess('');

    try {
      const response = await fetch('/api/admin/add-user', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(addUserForm),
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess(`User ${data.email} created successfully!`);
        setAddUserForm({ email: '', password: '', role: '' });
        fetchUsers(); // Refresh the user list
        toast({
          title: "Success",
          description: `User ${data.email} created successfully!`,
        });
      } else {
        setError(data.error || 'Failed to create user');
        toast({
          title: "Error",
          description: data.error || 'Failed to create user',
          variant: "destructive",
        });
      }
    } catch (error) {
      setError('Failed to create user');
      toast({
        title: "Error",
        description: 'Failed to create user',
        variant: "destructive",
      });
    } finally {
      setAddingUser(false);
    }
  };

  const handleDeleteUser = async (uid: string, email: string) => {
    if (!confirm(`Are you sure you want to delete user "${email}"? This action cannot be undone.`)) {
      return;
    }

    try {
      const response = await fetch('/api/admin/delete-user', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ uid }),
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess(`User ${email} deleted successfully`);
        fetchUsers(); // Refresh the user list
        toast({
          title: "Success",
          description: `User ${email} deleted successfully`,
        });
      } else {
        setError(data.error || 'Failed to delete user');
        toast({
          title: "Error",
          description: data.error || 'Failed to delete user',
          variant: "destructive",
        });
      }
    } catch (error) {
      setError('Failed to delete user');
      toast({
        title: "Error",
        description: 'Failed to delete user',
        variant: "destructive",
      });
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Unknown';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getRoleBadgeVariant = (role: string): "default" | "secondary" | "destructive" | "outline" => {
    switch (role) {
      case 'admin': return 'destructive';
      case 'manager': return 'default';
      case 'sales': return 'secondary';
      default: return 'outline';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="flex items-center space-x-2">
          <Loader2 className="w-6 h-6 animate-spin" />
          <span className="text-xl">Verifying admin access...</span>
        </div>
      </div>
    );
  }

  return (
    <SidebarProvider>
      <div className="min-h-screen flex w-full bg-background">
        {/* Sidebar */}
        <Sidebar className="w-64">
          <SidebarHeader className="p-6">
            <div className="flex items-center space-x-2">
              <Shield className="w-8 h-8 text-red-500" />
              <div>
                <h1 className="text-lg font-bold">Admin Panel</h1>
                <p className="text-sm text-muted-foreground">User Management</p>
              </div>
            </div>
          </SidebarHeader>
          <SidebarContent>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton
                  onClick={() => setActiveView('users')}
                  isActive={activeView === 'users'}
                  className="w-full justify-start"
                >
                  <Users className="w-4 h-4" />
                  <span>User Management</span>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton
                  onClick={() => setActiveView('analytics')}
                  isActive={activeView === 'analytics'}
                  className="w-full justify-start"
                >
                  <BarChart3 className="w-4 h-4" />
                  <span>Analytics</span>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarContent>
        </Sidebar>

        {/* Main Content */}
        <div className="flex-1 p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-4">
              <Button
                onClick={() => router.push('/')}
                variant="ghost"
                size="sm"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Dashboard
              </Button>
              <Separator orientation="vertical" className="h-6" />
              <div>
                <h1 className="text-2xl font-bold">
                  {activeView === 'users' ? 'User Management' : 'Analytics Dashboard'}
                </h1>
                <p className="text-muted-foreground">
                  {activeView === 'users' ? 'Manage system users and roles' : 'View system analytics and metrics'}
                </p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm text-muted-foreground">Logged in as:</p>
              <p className="font-semibold">{currentUser?.email}</p>
            </div>
          </div>

          {/* User Management View */}
          {activeView === 'users' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Add User Form */}
              <div className="lg:col-span-1">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <UserPlus className="w-5 h-5 mr-2" />
                      Add New User
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <form onSubmit={handleAddUser} className="space-y-4">
                      <div className="space-y-2">
                        <Label htmlFor="email">Email Address</Label>
                        <Input
                          id="email"
                          type="email"
                          placeholder="user@company.com"
                          value={addUserForm.email}
                          onChange={(e) => setAddUserForm(prev => ({ ...prev, email: e.target.value }))}
                          required
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="password">Password</Label>
                        <Input
                          id="password"
                          type="password"
                          placeholder="Enter secure password"
                          value={addUserForm.password}
                          onChange={(e) => setAddUserForm(prev => ({ ...prev, password: e.target.value }))}
                          minLength={6}
                          required
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="role">Role</Label>
                        <Select
                          value={addUserForm.role}
                          onValueChange={(value) => setAddUserForm(prev => ({ ...prev, role: value }))}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Select role" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="sales">Sales</SelectItem>
                            <SelectItem value="manager">Manager</SelectItem>
                            <SelectItem value="admin">Admin</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>

                      <Button
                        type="submit"
                        className="w-full"
                        disabled={addingUser}
                      >
                        {addingUser ? (
                          <>
                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                            Creating User...
                          </>
                        ) : (
                          <>
                            <UserPlus className="w-4 h-4 mr-2" />
                            Create User
                          </>
                        )}
                      </Button>
                    </form>
                  </CardContent>
                </Card>
              </div>

              {/* Users List */}
              <div className="lg:col-span-2">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <div className="flex items-center">
                        <Users className="w-5 h-5 mr-2" />
                        All Users ({users.length})
                      </div>
                      <Button
                        onClick={fetchUsers}
                        variant="outline"
                        size="sm"
                        disabled={loadingUsers}
                      >
                        {loadingUsers ? (
                          <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                          'Refresh'
                        )}
                      </Button>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {loadingUsers ? (
                      <div className="flex items-center justify-center py-8">
                        <Loader2 className="w-6 h-6 animate-spin mr-2" />
                        <span>Loading users...</span>
                      </div>
                    ) : users.length === 0 ? (
                      <div className="text-center py-8 text-muted-foreground">
                        No users found
                      </div>
                    ) : (
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Email</TableHead>
                            <TableHead>Role</TableHead>
                            <TableHead>Created</TableHead>
                            <TableHead className="w-[100px]">Actions</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {users.map((user) => (
                            <TableRow key={user.uid}>
                              <TableCell className="font-medium">{user.email}</TableCell>
                              <TableCell>
                                <Badge variant={getRoleBadgeVariant(user.role)}>
                                  {user.role.toUpperCase()}
                                </Badge>
                              </TableCell>
                              <TableCell className="text-muted-foreground">
                                {formatDate(user.createdAt)}
                              </TableCell>
                              <TableCell>
                                <Button
                                  onClick={() => handleDeleteUser(user.uid, user.email)}
                                  variant="ghost"
                                  size="sm"
                                  className="text-red-600 hover:text-red-700"
                                  disabled={user.uid === currentUser?.uid}
                                >
                                  <Trash2 className="w-4 h-4" />
                                </Button>
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    )}
                  </CardContent>
                </Card>
              </div>
            </div>
          )}

          {/* Analytics View */}
          {activeView === 'analytics' && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Users</CardTitle>
                  <Users className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{users.length}</div>
                  <p className="text-xs text-muted-foreground">
                    Active system users
                  </p>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Admins</CardTitle>
                  <Shield className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {users.filter(u => u.role === 'admin').length}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Admin users
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Managers</CardTitle>
                  <Settings className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {users.filter(u => u.role === 'manager').length}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Manager users
                  </p>
                </CardContent>
              </Card>
            </div>
          )}
        </div>
      </div>
    </SidebarProvider>
  );
}