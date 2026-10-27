import { Badge, Container, Group, Tabs, Title } from "@mantine/core";
import { useEffect, useState } from "react";

import { getHealth } from "./api/health";
import { AnalyticsPage } from "./features/analytics/AnalyticsPage";
import { DirectoryPage } from "./features/directory/DirectoryPage";

type BackendState = "checking" | "online" | "offline";

const BADGE_COLOR: Record<BackendState, string> = {
  checking: "gray",
  online: "green",
  offline: "red",
};

export default function App() {
  const [backend, setBackend] = useState<BackendState>("checking");

  useEffect(() => {
    getHealth()
      .then(() => setBackend("online"))
      .catch(() => setBackend("offline"));
  }, []);

  return (
    <Container size="xl" py="md">
      <Group justify="space-between">
        <Title order={2}>ACME Salary Management</Title>
        <Badge color={BADGE_COLOR[backend]}>Backend {backend}</Badge>
      </Group>
      <Tabs defaultValue="directory" mt="md" keepMounted={false}>
        <Tabs.List>
          <Tabs.Tab value="directory">Directory</Tabs.Tab>
          <Tabs.Tab value="analytics">Analytics</Tabs.Tab>
        </Tabs.List>
        <Tabs.Panel value="directory" pt="md">
          <DirectoryPage />
        </Tabs.Panel>
        <Tabs.Panel value="analytics" pt="md">
          <AnalyticsPage />
        </Tabs.Panel>
      </Tabs>
    </Container>
  );
}
