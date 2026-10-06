import React from "react";
import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { Button } from "@/components/ui/button";

describe("Button", () => {
  it("renders an accessible button with its label", () => {
    render(<Button>Start mission</Button>);
    expect(screen.getByRole("button", { name: "Start mission" })).toBeInTheDocument();
  });
});
